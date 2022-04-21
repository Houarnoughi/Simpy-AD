from turtle import color
from Location import Location
import simpy
from Colors import GREEN, END, RED
from Task import Task
import numpy as np
from Store import Store
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ProcessingUnit import ProcessingUnit
    from RoadSideUnit import RoadSideUnit

class Vehicle(object):
    idx = 0
    name = ''
    # c_location = []
    # f_location = []
    # speed = 0
    # task_list = []
    # PU_list = []

    def __init__(self,
                 c_location: Location,  # Current location: source
                 f_location: Location,  # Future location: destination
                 speed,  # The car speed
                 bw, # 4G bandwith to fog
                 task_list: List['Task'],  # The list of vehicle tasks
                 PU_list: List['ProcessingUnit'],  # The list of Processing units embedded on the vehicle
                 required_FPS,
                 env: simpy.Environment,  # The simulation environment
                 capacity=1):  # The capacity of the shared resource

        self.id = Vehicle.idx
        self.name = f'Vehicle-{Vehicle.idx}'
        Vehicle.idx += 1

        self.c_location = c_location
        self.f_location = f_location
        self.speed = speed
        self.bw = bw
        # keep track of all generated tasks
        self.all_tasks = []
        self.task_list = []
        self.setTaskList(task_list)
        self.required_FPS = required_FPS
        self.PU_list = []
        self.setPUList(PU_list)
        self.env = env
        self.capacity = capacity
        # self.updateTaskListExecution()
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
        STEP = 10
        trip_lat = np.linspace(self.c_location.latitude, self.f_location.latitude, STEP)
        trip_lon = np.linspace(self.c_location.longitude, self.f_location.longitude, STEP)

        #DEVIATION = 10
        #augm = lambda e: e + np.random.uniform(0,1)/DEVIATION
        #trip_lon = list(map(augm, trip_lon))
        #trip_lat = list(map(augm, trip_lat))

        trip = list(zip(trip_lat, trip_lon))

        #i = 0
        while True:
            #self.c_location.longitude = trip[i][0]
            #self.c_location.latitude = trip[i][1]
            #i += 1

            # sublit tasks to TaskMapper
            self.log(f"Generating tasks at {self.env.now}")
            for _ in range(self.required_FPS):
                for task in self.task_list:
                    t: 'Task' = Task(task.flop, task.size, task.criticality)
                    t.setCurrentVehicle(self)

                    # execution time in place
                    pu: ProcessingUnit = self.PU_list[0]
                    #DELTA = pu.getTaskExecutionTime(t) + pu.getTaskLoadingTime(t)
                    #DELTA = 1/self.required_FPS
                    DELTA = 1

                    # setting task deadline
                    t.setDeadline(self.env.now + DELTA)
                    # set expected exec time
                    t.setExpectedExecTime(DELTA)

                    #self.log(f"Generate Task {t} at {self.env.now}")

                    self.all_tasks.append(t)
                    Store.addTask(t)
                    
            # send all frame's tasks in a second
            yield self.env.timeout(1)

    def showInfo(self):
        print(
            f"{GREEN}Vehicle [{self.name}, PUs: {self.PU_list}, Tasks: {self.task_list} ]{END}")

    def log(self, message):
        print(f"{RED}[{self.name}] {message}{END}")

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
                task.setCurrentVehicle(self)
                self.task_list.append(task)
                self.log(f'[INFO] Vehicle-setTaskList: Task {task.getTaskName()} submitted to {self.getVehicleName()}')

    def setParent(self, parent):
        self.parent=parent
    
    def getParent(self):
        return self.parent

    # returns 1 PU (the first   )
    def getPU(self) -> 'ProcessingUnit':
        return self.PU_list[0]

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

                #TaskMapper.addPU(pu)
                self.log(f'[INFO] Vehicle-setPUList: Processing Unit {pu.getPUName()} added to {self.getVehicleName()}')

    def updateTaskListExecution(self):
        pu: ProcessingUnit = None
        for pu in self.getPUList():
            for task in pu.getTaskList():
                with pu.request() as req:
                    yield req
                    self.log(f'[LOG] Starting execution {task.getTaskName()} on {pu.getPUName()} at {self.env.now}')
                    # Multiply to adjust precision to simulation
                    execution_time = pu.getTaskExecutionTime(task) * 1000
                    yield self.env.timeout(execution_time)
                    self.log(f'[LOG] Finishing execution {task.getTaskName()} on {pu.getPUName()} at {self.env.now}')

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
