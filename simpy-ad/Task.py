from ProcessingUnit import ProcessingUnit
from TaskCriticality import TaskCriticality

class Task(object):
    CREATED = 0
    READY = 1
    QUEUED = 2
    INEXEC = 3
    SUCCESS = 4
    FAILED = 5
    CANCELED = 6
    PAUSED = 7
    RESUMED = 8
    FAILED_RESOURCE_UNAVAILABLE = 9

    idx = 0

    def __init__(self, flop, size, criticality: TaskCriticality=None, preemptive=False, real_time=False, status=PAUSED, currentVehicle=None,currentPU=None):
        self.id = Task.idx
        self.name = f'Task-{Task.idx}'
        Task.idx += 1
        self.criticality = criticality
        self.flop = flop
        self.remaining_flop = flop
        self.size = size
        self.preemptive = preemptive
        self.real_time = real_time
        self.status = status
        self.currentVehicle = currentVehicle
        self.currentPU = currentPU
        self.deadline = 0
        self.total_execution_time = 0
        self.execution_start_time = 0
        self.execution_end_time = 0

    def getTaskName(self):
        return self.name

    def getFlop(self):
        return self.flop

    def setFlop(self, flop):
        self.flop = flop

    def getSize(self):
        return self.size

    def setSize(self, size):
        self.size = size

    def getPreemptive(self):
        return self.preemptive

    def setPreemptive(self, preemptive):
        self.preemptive = preemptive

    def getRealTime(self):
        return self.real_time

    def setRealTime(self, realtime):
        self.real_time = realtime

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def getCurrentPU(self):
        return self.currentPU

    def setCurrentPU(self, pu: ProcessingUnit):
        self.currentPU = pu

    def getCurrentVehicle(self):
        return self.currentVehicle

    def setCurrentVehicle(self, current_vehicle):
        self.currentVehicle = current_vehicle

    # OS time
    def getTotalExecutionTime(self):
        #return self.total_execution_time
        return self.execution_end_time - self.execution_start_time
    
    # if ended after deadline (deadline fixed by Vehicle)
    def isFailed(self):
        return self.execution_end_time > self.deadline

    # 
    def isFinished(self):
        return self.remaining_flop <= 0

    def updateTotalExecutionTime(self, time):
        self.total_execution_time = self.getTotalExecutionTime() + time
    
    # OS time
    def setDeadline(self, deadline):
        self.deadline = deadline
    
    def getDeadline(self):
        return self.deadline

    def __str__(self):
        return f"[ID: {self.id}, {self.name}]"
    
    def __repr__(self) -> str:
        return f"[ID: {self.id}, {self.name}]"