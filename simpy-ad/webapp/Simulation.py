from threading import Thread, Condition
from multiprocessing import Process
from time import sleep
import simpy
import random

import sys
sys.path.append('.')

from CNNModel import CNNModel
from Task import _Task, TaskCriticality
import Store
from Location import Location
from Vehicle import Vehicle
from ProcessingUnit import AGX, TeslaV100
from RoadSideUnit import RoadSideUnit
from Server import Server
from TaskMapper import TaskMapper
import config

class Simulation(Thread):
    def __init__(self, steps=config.SIM_TIME, vehicle_count=config.VEHICLE_COUNT, vehicle_fps=config.FPS):
        Thread.__init__(self)
        self.EXIT_THREAD = False
        self.steps = steps
        self.vehicle_count = vehicle_count
        self.vehicle_fps = vehicle_fps

    def run(self):
        env = simpy.Environment()

        inception = CNNModel('Inception-v3', 1024)
        resnet18 = CNNModel('ResNet-18', 480)
        mobilenet = CNNModel('MobileNet0.25-v1', 240)

        vehicle_tasks = [
            _Task(flop=inception.getModelFLOPS(), size=inception.getModelMemory(), criticality=TaskCriticality.HIGH),
            #_Task(flop=resnet18.getModelFLOPS(), size=resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            #_Task(flop=mobilenet.getModelFLOPS(), size=mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
            #Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
            #Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            #Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
        ]
        for _ in range(self.vehicle_count):
            ## PU init
            pu1 = AGX(task_list=[], scheduler=config.EDGE_TASK_SCHEDULING_POLICY(config.AGX_QUANTUM), env=env)
            Store.Store.addPU(pu1)

            vehicle = Vehicle(
                c_location=Location("random", random.uniform(config.MIN_LAT, config.MAX_LAT), random.uniform(config.MIN_LONG, config.MAX_LONG)), 
                f_location=Location("Gare Lille", 50.63725143907785, 3.0702985651377745), 
                speed=10, 
                bw = 10e6,
                task_list=vehicle_tasks, 
                PU_list=[pu1], 
                required_FPS=self.vehicle_fps, 
                env=env)
            vehicle.showInfo()
            Store.Store.vehicle_list.append(vehicle)

        """
        RSU init  x5
        """
        locations = [
            Location("Zoo de Lille", 50.64099393427632, 3.044548801247785),
            Location("Jardin des Géants", 50.64347018158827, 3.0806523044990617),
            Location("Palais bx arts", 50.63222755233801, 3.0628195821035655),
            Location("Moulins", 50.620905648844506, 3.06973893974428),
            Location("wazemmes", 50.627218409442975, 3.0400339217074266)
        ]
        for i in range(config.RSU_COUNT):
            pu = TeslaV100(task_list=[], scheduler=config.FOG_TASK_SCHEDULING_POLICY(config.TESLA_QUANTUM), env=env)
            Store.Store.addPU(pu)

            rsu = RoadSideUnit(
                activity_range=100, 
                location=locations[i], 
                server_list=[
                    Server(pu_list=[pu], bw=1, env=env)
                ], 
                to_vehicle_bw=1, to_cloud_bw=1, env=env)
            rsu.showInfo()
            Store.Store.addRSU(rsu)

        taskMappingPolicy=config.TASK_MAPPING_POLICY(env=env)
        taskMapper = TaskMapper(env=env, taskMappingPolicy=taskMappingPolicy)

        while env.peek() < self.steps:
            if self.EXIT_THREAD:
                break

            env.step()
        
        Store.Store.showStats()
        Store.Store.clear()
    
    def stop(self):
        self.EXIT_THREAD = True

    def get_stats(self) -> float:
        print("Simulation store task count ", Store.Store.getTotalTaskCount(), id(Store.Store))
        return Store.Store.getTotalTaskCount()
    
    def test(self):
        print("test")

if __name__ == '__main__':
    s = Simulation()
    s.start()

    sleep(3)

    s.stop()
    