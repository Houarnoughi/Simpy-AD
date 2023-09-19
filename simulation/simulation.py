from .utils.network import Network
from .task_mapping.task_mapping_policy import TaskMappingPolicy
from .task_scheduling.task_scheduling_policy import TaskSchedulingPolicy
from .entity.processing_unit import ProcessingUnit

#from TaskMapper import TaskMapper
from .service.map_service import ORSPathPlanner
from .entity.server import Server
from .entity.road_side_unit import RoadSideUnit
from .entity.processing_unit import AGX, TeslaV100
from .entity.vehicle import Vehicle
from .entity.location import Location
from .store import Store
from .entity.task import Task, TaskCriticality
from .entity.cnn_model import CNNModel
from threading import Thread, Condition
from time import sleep
import simpy
import random

class Simulation(Thread):
    """
    Simulation is responsable for creating instances of
        - DataCenters (todo)
        - RSUs with rsu_locations
            * pu
            * server(pu)
        - Vehicles with vehicle_count
            * scheduler
            * pu(scheduler)
            * List of task names
        
        Vehicles are responsable for creating tasks based on task_list (task names) on runtime
    """
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
        vehicle_network: Network,
        # RSU
        rsu_count: int,
        rsu_even_distribution: bool,
        rsu_processing_unit: ProcessingUnit,
        rsu_scheduling: TaskSchedulingPolicy,
        rsu_network: Network,
        # DATACENTER
        datacenter_count: int,
        datacenter_processing_unit: ProcessingUnit,
        datacenter_scheduling: TaskSchedulingPolicy,
        datacenter_network: Network,
        # scheduler
        SCHEDULER_QUANTUM: float
    ):
        Thread.__init__(self)
        self.EXIT_THREAD = False

        self.steps: int = steps - 0.0000000001
        self.town: dict = town
        self.radius: int = radius

        self.vehicle_count: int = vehicle_count
        self.vehicle_fps: int = vehicle_fps
        self.vehicle_tasks = vehicle_tasks
        self.vehicle_processing_unit = vehicle_processing_unit
        self.vehicle_mapping = vehicle_mapping
        self.vehicle_scheduling = vehicle_scheduling
        self.vehicle_network = vehicle_network

        self.rsu_count: int = rsu_count
        self.rsu_processing_unit = rsu_processing_unit
        self.rsu_even_distribution = rsu_even_distribution
        self.rsu_scheduling = rsu_scheduling
        self.rsu_network = rsu_network

        self.datacenter_count: int = datacenter_count
        self.datacenter_processing_unit = datacenter_processing_unit
        self.datacenter_scheduling = datacenter_scheduling
        self.datacenter_network = datacenter_network

        self.SCHEDULER_QUANTUM = SCHEDULER_QUANTUM

        self.env = simpy.Environment()

    def run(self):

        # RSU
        print("Getting RSU locations")
        rsu_locations = Location.getLocations(
            town=self.town, 
            count=self.rsu_count, 
            radius=self.radius,
            evenDistribution=self.rsu_even_distribution
        )
        print("Done ...")

        for location in rsu_locations:
            scheduler: TaskSchedulingPolicy = self.rsu_scheduling(self.SCHEDULER_QUANTUM)
            pu = self.rsu_processing_unit(scheduler=scheduler, env=self.env)
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
            scheduler: TaskSchedulingPolicy = self.vehicle_scheduling(self.SCHEDULER_QUANTUM)
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
                path_planner=ORSPathPlanner(),
                task_mapping_policy=self.vehicle_mapping(env=self.env),
                required_FPS=self.vehicle_fps,
                env=self.env)
            vehicle.showInfo()
            Store.addVehicle(vehicle)

        #taskMappingPolicy = self.vehicle_mapping(env=self.env)
        #taskMapper = TaskMapper(env=self.env, taskMappingPolicy=taskMappingPolicy)

        STOP = False
        #while self.env.peek() < self.steps:
        while True:
            if self.EXIT_THREAD:
                break

            self.env.step()

            self.checkVehiclesDone()
            self.checkSteps()

        Store.showStats()
        Store.clear()
    
    def checkSteps(self):
        if self.env.now > self.steps:
            print(f"Stopping {self.steps} steps done")
            self.EXIT_THREAD = True
    
    # returns True if vehicles finished their trip
    def checkVehiclesDone(self):
        vehicles = Store.vehicle_list

        for v in vehicles:
            v: Vehicle = v
            if v.isStillRunning():
                #print("still running")
                return

        print("Stopping Simulation thread, all vehicles' trips done")
        self.EXIT_THREAD = True

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
