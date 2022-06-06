import config
from Networking import Network
from TaskMappingPolicy import TaskMappingPolicy
from TaskSchedulingPolicy import TaskSchedulingPolicy
from ProcessingUnit import ProcessingUnit

from TaskMapper import TaskMapper
from Server import Server
from RoadSideUnit import RoadSideUnit
from ProcessingUnit import AGX, TeslaV100
from Vehicle import Vehicle
from Location import Location
import Store
from Task import Task, TaskCriticality
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
        # Simulation
        steps,
        town: dict,
        radius,
        # Vehicle
        vehicle_count,
        vehicle_fps,
        vehicle_tasks: list[Task],
        vehicle_processing_unit: ProcessingUnit,
        vehicle_mapping: TaskMappingPolicy,
        vehicle_scheduling: TaskSchedulingPolicy,
        vehicle_networking: Network,
        # RSU
        rsu_count,
        rsu_even_distribution: bool,
        rsu_processing_unit: ProcessingUnit,
        rsu_scheduling: TaskSchedulingPolicy,
        rsu_networking: Network,
        # DATACENTER
        datacenter_count,
        datacenter_processing_unit: ProcessingUnit,
        datacenter_scheduling: TaskSchedulingPolicy,
        datacenter_networking: Network,
    ):
        Thread.__init__(self)
        self.EXIT_THREAD = False

        self.steps = steps
        self.town = town
        self.radius = radius

        self.vehicle_count = vehicle_count
        self.vehicle_fps = vehicle_fps
        self.vehicle_tasks = vehicle_tasks
        self.vehicle_processing_unit = vehicle_processing_unit
        self.vehicle_mapping = vehicle_mapping
        self.vehicle_scheduling = vehicle_scheduling
        self.vehicle_networking = vehicle_networking

        self.rsu_count = rsu_count
        self.rsu_processing_unit = rsu_processing_unit
        self.rsu_even_distribution = rsu_even_distribution
        self.rsu_scheduling = rsu_scheduling
        self.rsu_networking = rsu_networking

        self.datacenter_count = datacenter_count
        self.datacenter_processing_unit = datacenter_processing_unit
        self.datacenter_scheduling = datacenter_scheduling
        self.datacenter_networking = datacenter_networking

        self.env = simpy.Environment()

    def run(self):

        # RSU
        rsu_locations = Location.getLocations(
            town=self.town, 
            count=self.rsu_count, 
            radius=self.radius,
            evenDistribution=self.rsu_even_distribution
        )

        for location in rsu_locations:
            pu = config.RSU_PROCESSING_UNIT(scheduler=self.rsu_scheduling(config.TESLA_QUANTUM), env=self.env)
            Store.Store.addPU(pu)

            rsu = RoadSideUnit(
                activity_range=100,
                location=location,
                server_list=[
                    Server(pu_list=[pu], bw=1, env=self.env)
                ],
                to_vehicle_bw=1, to_cloud_bw=1, env=self.env)
            rsu.showInfo()
            Store.Store.addRSU(rsu)
        
        # Vehicle
        inception = CNNModel('Inception-v3', 1024)
        resnet18 = CNNModel('ResNet-18', 480)
        mobilenet = CNNModel('MobileNet0.25-v1', 240)

        vehicle_tasks = [
            #Task(flop=inception.getModelFLOPS(), size=inception.getModelMemory(), criticality=TaskCriticality.HIGH),
            #Task(flop=resnet18.getModelFLOPS(), size=resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            Task(flop=mobilenet.getModelFLOPS(), size=mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
            #Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
            #Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            #Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
        ]
        for _ in range(self.vehicle_count):
            # PU init
            scheduler = self.vehicle_scheduling(config.AGX_QUANTUM)
            pu = config.VEHICLE_PROCESSING_UNIT(scheduler=scheduler, env=self.env)
            Store.Store.addPU(pu)

            vehicle = Vehicle(
                c_location=Location.getLocationInRange(
                    self.town, random.randint(0, self.radius)),
                f_location=Location.getLocationInRange(
                    self.town, random.randint(0, self.radius)),
                # f_location=self.town,
                speed=10,
                bw=10e6,
                task_list=vehicle_tasks,
                PU_list=[pu],
                required_FPS=self.vehicle_fps,
                env=self.env)
            vehicle.showInfo()
            Store.Store.vehicle_list.append(vehicle)

        taskMappingPolicy = self.vehicle_mapping(env=self.env)
        taskMapper = TaskMapper(
            env=self.env, taskMappingPolicy=taskMappingPolicy)

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
