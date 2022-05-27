import sched
from Networking import Network
from TaskMappingPolicy import TaskMappingPolicy
from TaskSchedulingPolicy import TaskSchedulingPolicy
import config
from TaskMapper import TaskMapper
from Server import Server
from RoadSideUnit import RoadSideUnit
from ProcessingUnit import AGX, TeslaV100
from Vehicle import Vehicle
from Location import Location
import Store
from Task import _Task, TaskCriticality
from CNNModel import CNNModel
from threading import Thread, Condition
from multiprocessing import Process
from time import sleep
import simpy
import random

import sys
sys.path.append('.')


class Simulation(Thread):
    def __init__(
        self, 
        steps,
        vehicle_count,
        vehicle_fps,
        vehicle_mapping: TaskMappingPolicy,
        vehicle_scheduling: TaskSchedulingPolicy,
        vehicle_networking: Network,
        town: dict,
        radius = 3
    ):
        Thread.__init__(self)
        self.EXIT_THREAD = False
        self.steps = steps
        self.vehicle_count = vehicle_count
        self.vehicle_fps = vehicle_fps
        self.vehicle_mapping = vehicle_mapping
        self.vehicle_scheduling = vehicle_scheduling
        self.vehicle_networking = vehicle_networking
        self.town = town
        self.radius = radius
        self.env = simpy.Environment()

    def run(self):
        
        inception = CNNModel('Inception-v3', 1024)
        resnet18 = CNNModel('ResNet-18', 480)
        mobilenet = CNNModel('MobileNet0.25-v1', 240)

        vehicle_tasks = [
            _Task(flop=inception.getModelFLOPS(), size=inception.getModelMemory(
            ), criticality=TaskCriticality.HIGH),
            #_Task(flop=resnet18.getModelFLOPS(), size=resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            #_Task(flop=mobilenet.getModelFLOPS(), size=mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
            #Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
            #Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            #Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
        ]
        for _ in range(self.vehicle_count):
            # PU init
            scheduler = self.vehicle_scheduling(config.AGX_QUANTUM)
            pu1 = AGX(task_list=[], scheduler=scheduler, env=self.env)
            Store.Store.addPU(pu1)

            vehicle = Vehicle(
                c_location=Location.getLocationInRange(self.town, random.randint(0, self.radius)),
                f_location=Location.getLocationInRange(self.town, random.randint(0, self.radius)),
                #f_location=self.town,
                speed=10,
                bw=10e6,
                task_list=vehicle_tasks,
                PU_list=[pu1],
                required_FPS=self.vehicle_fps,
                env=self.env)
            vehicle.showInfo()
            Store.Store.vehicle_list.append(vehicle)

        """
        RSU init  x5
        """
        locations = [
            Location("Zoo de Lille", 50.64099393427632, 3.044548801247785),
            Location("Jardin des Géants",
                     50.64347018158827, 3.0806523044990617),
            Location("Palais bx arts", 50.63222755233801, 3.0628195821035655),
            Location("Moulins", 50.620905648844506, 3.06973893974428),
            Location("wazemmes", 50.627218409442975, 3.0400339217074266)
        ]
        for i in range(config.RSU_COUNT):
            pu = TeslaV100(task_list=[], scheduler=config.FOG_TASK_SCHEDULING_POLICY(
                config.TESLA_QUANTUM), env=self.env)
            Store.Store.addPU(pu)

            rsu = RoadSideUnit(
                activity_range=100,
                location=locations[i],
                server_list=[
                    Server(pu_list=[pu], bw=1, env=self.env)
                ],
                to_vehicle_bw=1, to_cloud_bw=1, env=self.env)
            rsu.showInfo()
            Store.Store.addRSU(rsu)

        taskMappingPolicy = self.vehicle_mapping(env=self.env)
        taskMapper = TaskMapper(env=self.env, taskMappingPolicy=taskMappingPolicy)

        while self.env.peek() < self.steps:
            if self.EXIT_THREAD:
                break

            self.env.step()

        Store.Store.showStats()
        Store.Store.clear()

    def stop(self):
        self.EXIT_THREAD = True

    def get_stats(self) -> float:
        print("Simulation store task count ",
              Store.Store.getTotalTaskCount(), id(Store.Store))
        return Store.Store.getTotalTaskCount()

    def test(self):
        print("test")


if __name__ == '__main__':
    s = Simulation()
    s.start()

    sleep(3)

    s.stop()
