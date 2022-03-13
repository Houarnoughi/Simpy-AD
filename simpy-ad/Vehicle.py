from Location import Location
import simpy
from TaskMapper import TaskMapper
from Colors import GREEN, END, RED
from Task import Task


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
                 task_list,  # The list of vehicle tasks
                 PU_list,  # The list of Processing units embedded on the vehicle
                 required_FPS,
                 env: simpy.Environment,  # The simulation environment
                 capacity=1):  # The capacity of the shared resource

        self.id = Vehicle.idx
        self.name = f'Vehicle-{Vehicle.idx}'
        Vehicle.idx += 1

        self.c_location = c_location
        self.f_location = f_location
        self.speed = speed
        # self.task_list = task_list
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
    """

    def run(self):
        while True:
            # sublit tasks to TaskMapper
            for _ in range(self.required_FPS):
                for task in self.task_list:
                    t = Task(task.flop, task.size, task.criticality)
                    t.currentVehicle = self
                    #t = task
                    self.log(f"Generate Task {t} at {self.env.now}")
                    TaskMapper.addTask(t)

                    # send 1 task
                    yield self.env.timeout(1)

                # send frame's tasks
                # yield self.env.timeout(1)

            # send all frame's tasks
            # yield self.env.timeout(1)

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

    # Get the source location of the vehicle
    def getCurrentLocation(self):
        return self.c_location

    # Set the source location of the vehicle
    def setCurrentLocation(self, location):
        self.c_location = location

    # Get the destination location
    def getFutureLocation(self):
        return self.f_location

    # Set the destination location
    def setFutureLocation(self, location):
        self.f_location = location

    # Get the average car driving speed
    def getSpeed(self):
        return self.speed

    # Set the average car driving speed
    def setSpeed(self, speed):
        self.speed = speed

    # Get the task list assigned to the vehicle
    def getTaskList(self):
        return self.task_list

    # Assign the Task list to be executed by the vehicle
    def setTaskList(self, task_list):
        for task in task_list:
            if task not in self.task_list:
                task.setCurrentVehicle(self)
                self.task_list.append(task)
                self.log(f'[INFO] Vehicle-setTaskList: Task {task.getTaskName()} submitted to {self.getVehicleName()}')

    # Get the list of Processing Units assigned embedded in the vahicle
    def getPUList(self):
        return self.PU_list

    # Assign the Processing Unit list to the vehicle
    def setPUList(self, PU_list):
        for pu in PU_list:
            if pu not in self.getPUList():
                pu.setCurrentCurrentVehicle(self)
                self.PU_list.append(pu)

                TaskMapper.addPU(pu)
                self.log(f'[INFO] Vehicle-setPUList: Processing Unit {pu.getPUName()} added to {self.getVehicleName()}')

    def updateTaskListExecution(self):
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
    def getClosestRSU(self, rsu_list):
        closest_rsu = None
        min_distance = float("inf")

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
