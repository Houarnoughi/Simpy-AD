import simpy
from simulation import config
from simulation.entity.location import Location
from simulation.utils.colors import GREEN, END, RED
from simulation.entity.task import Task, getTaskInstanceByName
from typing import List, TYPE_CHECKING
from simulation.entity.processing_unit import AGX
from simulation.service.map_service import PathPlanner
from simulation.task_mapping import TaskMappingPolicy
from simulation.store import Store

if TYPE_CHECKING:
    from entity.processing_unit import ProcessingUnit
    from entity.road_side_unit import RoadSideUnit


class Vehicle(object):
    idx = 0

    def __init__(self,
                 c_location: Location,  # Current location: source
                 f_location: Location,  # Future location: destination
                 speed,  # The car speed
                 bw, # 4G bandwith to fog
                 task_list: List['Task'],  # The list of vehicle tasks
                 PU_list: List['ProcessingUnit'],  # The list of Processing units embedded on the vehicle
                 task_mapping_policy: TaskMappingPolicy,
                 required_FPS,
                 env: simpy.Environment,  # The simulation environment
                 capacity=1):  # The capacity of the shared resource

        self.id = Vehicle.idx
        self.name = f'Vehicle-{Vehicle.idx}'
        Vehicle.idx += 1

        self.c_location = c_location
        self.f_location = f_location
        self.trip_coordinates = list()
        self.trip_finished = False
        self.speed = speed
        self.bw = bw
        self.env = env
        # keep track of all generated tasks
        self.all_tasks = list()
        self.task_list = task_list
        #self.setTaskList(task_list)
        self.required_FPS = required_FPS
        self.PU_list = list()
        self.setPUList(PU_list)

        self.task_mapping_policy = task_mapping_policy
        self.capacity = capacity
        # simpy.Resource.__init__(self, env, capacity)
        self.run = env.process(self.run())

    """
    Send runtime tasks to TaskMapper

    DELTA is set in respect to required FPS
    to get a positive reward if success and negative reward if failure

    The goal is to approach FPS by training
    """
    def run(self):
        DELTA = 0

        # generate trip coordinates
        self.log("Getting path")
        self.trip_coordinates = PathPlanner.getPath(self.c_location, self.f_location)
        self.log(f'Trip Coordinates length {len(self.trip_coordinates)}')
       
        while not self.trip_finished:
            # sublit tasks to TaskMapper
            # random.randint(10, 30)#self.required_FPS - random.randint(10, 30)
            FPS = self.required_FPS
            for frame in range(FPS):
                for i, task_name in enumerate(self.task_list):
                    #print("taskClass", taskClass)
                    #t: 'Task' = Task(flop=task.flop, size=task.size, criticality=task.criticality)
                    task: 'Task' =  getTaskInstanceByName(task_name)
                    #print(f"task {task.getInfos()}")
                    task.setCurrentVehicle(self)

                    # execution time in place
                    pu: ProcessingUnit = self.PU_list[0]
                    EXPECTED_EXEC_TIME = pu.getTaskExecutionTime(task) + pu.getTaskLoadingTime(task) 
                    #t.setExpectedExecTime(EXPECTED_EXEC_TIME)
                    DEADLINE = self.env.now + EXPECTED_EXEC_TIME

                    # get from pu directly without 
                    DELTA = pu.getCycle()
                    task.setDeadline(DEADLINE + DELTA)
                    
                    self.all_tasks.append(task)
                    Store.addTask(task)

                    sorted_pu_list = Store.getClosestPUforTask(
                        task=task,
                        n=config.N_CLOSEST_PU,
                        OFFLOAD_TO_RSU=config.OFFLOAD_TO_RSU,
                        OFFLOAD_TO_DATACENTER=config.OFFLOAD_TO_DATACENTER
                    )
                    sorted_pu_list.append(pu)
                    #print("sorted_pu_list", sorted_pu_list)

                    self.task_mapping_policy.assignToPu(task, sorted_pu_list)
                    """
                    #self.log(f'task deadline {t} {t.getDeadline()}')
                    #TIMEOUT = 1 / (FPS*len(self.task_list))
                    #yield self.env.timeout(TIMEOUT)
                    """
                # send frame's tasks
                TIMEOUT = 1 / FPS
                yield self.env.timeout(TIMEOUT)

                #self.log(f"Generated {len(self.task_list)} tasks, TIMEOUT {TIMEOUT}, Store: to execute {Store.getTasksToExecuteCount()}, incomplete {Store.getIncompleteTasksCount()}")
                #yield self.env.timeout(TIMEOUT)
            try:
                self.move()
            except IndexError:
                self.log("Trip Finished")
                self.trip_finished = True
                break

    def getTripCoordinates(self) -> List:
        return self.trip_coordinates

    def isStillRunning(self):
        return not self.trip_finished

    def isTripFinished(self):
        return self.trip_finished

    def move(self):
        """
        Moves to next coordinates tuple according to speed
        From current location to 
        """
        current_location = self.getCurrentLocation().getLatitudeLongitude()
        long, lat = self.trip_coordinates.pop(0)
        future_location = Location("", lat, long)
        #distance = Location.getDistanceInKmFromTuples(current_location, new_location)

        self.setCurrentLocation(future_location)

    def showInfo(self):
        print(
            f"{GREEN}Vehicle [{self.name}, PUs: {self.PU_list}, Tasks: {self.task_list} ]{END}")

    def log(self, message):
        print(f"{END}{self.env.now}: {RED}[{self.name}] {message}{END}")

    # Get the name of the vehicle
    def getVehicleName(self):
        return self.name

    # Set the name of the vehicle
    def setVehicleName(self, name):
        self.name = name

    def getLocation(self) -> Location:
        return self.c_location

    # Get the source location of the vehicle
    def getCurrentLocation(self) -> Location:
        return self.c_location

    # Set the source location of the vehicle
    def setCurrentLocation(self, location: Location):
        self.c_location = location

    # Get the destination location
    def getFutureLocation(self) -> Location:
        return self.f_location

    # Set the destination location
    def setFutureLocation(self, location: Location):
        self.f_location = location

    # Get the average car driving speed
    def getSpeed(self):
        return self.speed

    # Set the average car driving speed
    def setSpeed(self, speed):
        self.speed = speed

    # Get the task list assigned to the vehicle
    def getTaskList(self) -> List['Task']:
        return self.task_list

    # Assign the Task list to be executed by the vehicle
    def setTaskList(self, task_list: List['Task']):
        task: 'Task' = None
        for task in task_list:
            if task not in self.task_list:
                task.setCurrentVehicle(vehicle=self)
                self.task_list.append(task)
                self.log(
                    f'[INFO] Vehicle-setTaskList: Task {task.getTaskName()} submitted to {self.getVehicleName()}')

    def setParent(self, parent):
        self.parent = parent

    def getParent(self):
        return self.parent

    # returns vehicle's main PU (AGX)
    def getPU(self) -> 'ProcessingUnit':
        for pu in self.PU_list:
            if isinstance(pu, AGX):
                return pu
        #return self.PU_list[0]

    # Get the list of Processing Units assigned embedded in the vahicle
    def getPUList(self) -> List['ProcessingUnit']:
        return self.PU_list

    # Assign the Processing Unit list to the vehicle
    def setPUList(self, PU_list: List['ProcessingUnit']):
        pu: ProcessingUnit = None
        for pu in PU_list:
            if pu not in self.getPUList():
                pu.setCurrentCurrentVehicle(self)
                self.PU_list.append(pu)

                pu.setParent(self)

                # TaskMapper.addPU(pu)
                self.log(
                    f'[INFO] Vehicle-setPUList: Processing Unit {pu.getPUName()} added to {self.getVehicleName()}')

    # Get the closest RSU among the list of all RSUs
    def getClosestRSU(self, rsu_list: List['RoadSideUnit']) -> 'RoadSideUnit':
        closest_rsu: RoadSideUnit = None
        min_distance = float("inf")

        rsu: RoadSideUnit = None
        for rsu in rsu_list:
            rsu_location = rsu.getLocation()
            dist_to_rsu = self.getCurrentLocation().getDistanceInKm(rsu_location)
            if dist_to_rsu <= min_distance:
                min_distance = dist_to_rsu
                closest_rsu = rsu

        return closest_rsu

    # Get the frame rate required by the application. It depends on the car speed
    # https://www.automate.org/industry-insights/vision-navigates-obstacles-on-the-road-to-autonomous-vehicles
    def getRequiredFPS(self):
        return self.required_FPS

    # Get the required inference latency based on the FPS
    def getRequiredLatency(self):
        return 1/self.getRequiredFPS()

    # Get the distance to be explored by the vehicle
    def getTripDistanceInKm(self):
        return self.getCurrentLocation().getDistanceInKm(self.getFutureLocation())

    # Get the duration of the trip depending on the car speed
    def getTripDurationInSeconds(self):
        return (self.getTripDistanceInKm() / self.getSpeed()) * 3600

    # Get the number of frames (inferences) to be executed during the trip
    # It depends on the FPS required by the task and the car speed/trip duration
    def getFramesToBeProcessed(self):
        return int(self.getTripDurationInSeconds() * self.getRequiredFPS())

    def __str__(self):
        return f"[ID: {self.id}, {self.name}]"

    def __repr__(self) -> str:
        return f"[ID: {self.id}, {self.name}]"
