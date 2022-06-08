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
from Store import Store
from Task import Task, TaskCriticality
from CNNModel import CNNModel
from threading import Thread, Condition
from time import sleep
import simpy
import random

import sys
sys.path.append('.')


class Simulation(Thread):
    def __init__(
        self,
        # Simulation
        steps: int,
        town: dict,
        radius: int,
        # Vehicle
        vehicle_count: int,
        vehicle_fps: int,
        vehicle_tasks: list[Task],
        vehicle_processing_unit: ProcessingUnit,
        vehicle_mapping: TaskMappingPolicy,
        vehicle_scheduling: TaskSchedulingPolicy,
        vehicle_networking: Network,
        # RSU
        rsu_count: int,
        rsu_even_distribution: bool,
        rsu_processing_unit: ProcessingUnit,
        rsu_scheduling: TaskSchedulingPolicy,
        rsu_networking: Network,
        # DATACENTER
        datacenter_count: int,
        datacenter_processing_unit: ProcessingUnit,
        datacenter_scheduling: TaskSchedulingPolicy,
        datacenter_networking: Network,
    ):
        Thread.__init__(self)
        self.EXIT_THREAD = False

        self.steps: int = steps
        self.town: dict = town
        self.radius: int = radius

        self.vehicle_count: int = vehicle_count
        self.vehicle_fps: int = vehicle_fps
        self.vehicle_tasks = vehicle_tasks
        self.vehicle_processing_unit = vehicle_processing_unit
        self.vehicle_mapping = vehicle_mapping
        self.vehicle_scheduling = vehicle_scheduling
        self.vehicle_networking = vehicle_networking

        self.rsu_count: int = rsu_count
        self.rsu_processing_unit = rsu_processing_unit
        self.rsu_even_distribution = rsu_even_distribution
        self.rsu_scheduling = rsu_scheduling
        self.rsu_networking = rsu_networking

        self.datacenter_count: int = datacenter_count
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
            pu = self.rsu_processing_unit(scheduler=self.rsu_scheduling(config.TESLA_QUANTUM), env=self.env)
            Store.addPU(pu)

            rsu = RoadSideUnit(
                activity_range=100,
                location=location,
                server_list=[
                    Server(pu_list=[pu], bw=1, env=self.env)
                ],
                to_vehicle_bw=1, to_cloud_bw=1, env=self.env)
            rsu.showInfo()
            Store.addRSU(rsu)
        
        # Vehicle
        vehicle_tasks = self.vehicle_tasks #[task() for task in self.vehicle_tasks]

        for _ in range(self.vehicle_count):
            # PU init
            scheduler = self.vehicle_scheduling(config.AGX_QUANTUM)
            pu = self.vehicle_processing_unit(scheduler=scheduler, env=self.env)
            Store.addPU(pu)

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
                task_mapping_policy=self.vehicle_mapping(env=self.env),
                required_FPS=self.vehicle_fps,
                env=self.env)
            vehicle.showInfo()
            Store.addVehicle(vehicle)

        #taskMappingPolicy = self.vehicle_mapping(env=self.env)
        #taskMapper = TaskMapper(env=self.env, taskMappingPolicy=taskMappingPolicy)

        while self.env.peek() < self.steps:
            if self.EXIT_THREAD:
                break

            self.env.step()

        Store.showStats()
        #Store.clear()

    def stop(self):
        self.EXIT_THREAD = True

    def get_stats(self) -> float:
        print("Simulation store task count ",
              Store.getTotalTaskCount(), id(Store))
        return Store.getTotalTaskCount()

    def test(self):
        print("test")


if __name__ == '__main__':
    s = Simulation()
    s.start()

    sleep(3)

    s.stop()
