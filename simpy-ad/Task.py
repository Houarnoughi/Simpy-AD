from ProcessingUnit import ProcessingUnit
from TaskCriticality import TaskCriticality
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Vehicle import Vehicle

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
        # deadline and expected execution time for failure check
        self.deadline = 0
        self.expected_exec_time = 0
        self.total_execution_time = 0
        self.execution_start_time = -1
        self.execution_end_time = -1

        self.scheduler_rounds = 0
        
    def isStarted(self):
        return self.execution_start_time != -1
    
    def isFinished(self):
        return self.execution_end_time != -1
    
    def isFinishedBeforeDeadline(self):
        return self.execution_end_time < self.deadline

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

    def getCurrentPU(self) -> ProcessingUnit:
        return self.currentPU

    def setCurrentPU(self, pu: ProcessingUnit):
        self.currentPU = pu

    def getCurrentVehicle(self) -> 'Vehicle':
        return self.currentVehicle

    def setCurrentVehicle(self, current_vehicle: 'Vehicle'):
        self.currentVehicle = current_vehicle

    # OS time
    def getTotalExecutionTime(self):
        #return self.total_execution_time
        return self.execution_end_time - self.execution_start_time
    
    def updateTotalExecutionTime(self, time):
        self.total_execution_time = self.getTotalExecutionTime() + time
    
    # Simpy time
    def setDeadline(self, deadline):
        self.deadline = deadline
    
    def getDeadline(self):
        return self.deadline

    # Simpy time
    def setExpectedExecTime(self, time):
        self.expected_exec_time = time
    
    def getExpectedExecTime(self):
        return self.expected_exec_time

    def __str__(self):
        return f"[ID: {self.id}, {self.name}]"
    
    def __repr__(self) -> str:
        return f"[ID: {self.id}, {self.name}]"