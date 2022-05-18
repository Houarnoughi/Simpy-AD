from logging import critical
from TaskCriticality import TaskCriticality
from typing import TYPE_CHECKING
from enum import Enum
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from Vehicle import Vehicle
    from ProcessingUnit import ProcessingUnit


class TaskStatus(Enum):
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


class _Task(ABC):
    """
    Abstract class for defining tasks

    Task 
        - is created on a vehicle
        - is assigned to a PU to be executed
        - flop is the amount of computation
        - remaining_flop is the amount to execute, modified by PU
        - size is task's memory footprint
        - execution_start_time is Simpy time of when PU started executing the task
        - execution_end_time is Simpy time set when there's no more remaining_flop to execute
        - scheduler_rounds is the number of times a task's been through the TaskScheduler (Round Robin)
    """
    idx = 0

    def __init__(self, vehicle: 'Vehicle' = None, deadline=0, pu: 'ProcessingUnit' = None, flop: float = 0, size: float = 0, criticality: TaskCriticality = None):
        self.id = _Task.idx
        self.name = f'Task-{self.id}'
        _Task.idx += 1

        # parent
        self.vehicle: 'Vehicle' = vehicle

        self.status: TaskStatus = None
        self.pu: 'ProcessingUnit' = pu

        # props
        self.flop: float = flop
        self.remaining_flop: float = flop
        self.size: float = size
        self.criticality: TaskCriticality = criticality

        # execution
        self.deadline: float = deadline
        self.execution_start_time: float = -1
        self.execution_end_time: float = -1

        # scheduler
        self.scheduler_rounds = 0

    # for stats
    def isSuccess(self):
        return self.isStarted() and self.isFinished() and self.isFinishedBeforeDeadline()

    def isFailed(self):
        return (self.isStarted() and self.isFinished()) and not self.isFinishedBeforeDeadline()

    def isIncomplete(self):
        return self.isStarted() and not self.isFinished()

    def isStarted(self):
        return self.execution_start_time != -1

    def isFinished(self):
        return self.execution_end_time != -1

    def isFinishedBeforeDeadline(self):
        return self.execution_end_time <= self.deadline

    def setCurrentVehicle(self, vehicle: 'Vehicle'):
        self.vehicle = vehicle

    def getCurrentVehicle(self) -> 'Vehicle':
        return self.vehicle

    def setFlop(self, flop: float):
        self.flop = flop

    def getFlop(self) -> float:
        return self.flop

    def setRemainingFlop(self, flop: float):
        self.flop = flop

    def decreaseRemainingFlop(self, flop: float):
        self.remaining_flop -= flop

    def getRemainingFlop(self) -> float:
        return self.remaining_flop

    def setSize(self, size: float):
        self.size = size

    def getSize(self) -> float:
        return self.size

    def setDeadline(self, deadline: float):
        self.deadline = deadline

    def getDeadline(self) -> float:
        return self.deadline
    
    def getCriticality(self) -> TaskCriticality:
        return self.criticality

    def setStatus(self, status: TaskStatus):
        self.status = status

    def getStatus(self) -> TaskStatus:
        return self.status

    def setCurrentPu(self, pu: 'ProcessingUnit'):
        self.pu = pu

    def getCurrentPu(self) -> 'ProcessingUnit':
        return self.pu

    def setExecutionStartTime(self, time: float):
        self.execution_start_time = time

    def getExecutionStartTime(self) -> float:
        return self.execution_start_time

    def setExecutionEndTime(self, time: float):
        self.execution_end_time = time

    def getExecutionEndTime(self) -> float:
        return self.execution_end_time

    def addSchedulerRound(self):
        self.scheduler_rounds += 1

    def getSchedulerRounds(self) -> int:
        return self.scheduler_rounds

    def getTaskName(self) -> str:
        return self.name

    def getInfos(self) -> str:
        return f'[{self.name}, flop={self.flop}, remainingFlop={self.remaining_flop}, size={self.size}, startTime={self.execution_start_time}, endTime={self.execution_end_time}, pu={self.pu}, vehicle={self.vehicle}, status={self.status}, rounds={self.scheduler_rounds}]'

    def __repr__(self) -> str:
        return f'[{self.name}, {self.pu}]'


class Task(object):

    idx = 0

    def __init__(self, flop, size, criticality: TaskCriticality = None, preemptive=False, real_time=False, status=TaskStatus.PAUSED, currentVehicle=None, currentPU=None):
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

    def isSuccess(self):
        return self.isStarted() and self.isFinished() and self.isFinishedBeforeDeadline()

    def isFailed(self):
        return (self.isStarted() and self.isFinished()) and not self.isFinishedBeforeDeadline()

    def isIncomplete(self):
        return self.isStarted() and not self.isFinished()

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

    def getCurrentPU(self) -> 'ProcessingUnit':
        return self.currentPU

    def setCurrentPU(self, pu: 'ProcessingUnit'):
        self.currentPU = pu

    def getCurrentVehicle(self) -> 'Vehicle':
        return self.currentVehicle

    def setCurrentVehicle(self, current_vehicle: 'Vehicle'):
        self.currentVehicle = current_vehicle

    # OS time
    def getTotalExecutionTime(self):
        # return self.total_execution_time
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

# if __name__ == '__main__':
#     tasks = [_Task() for i in range(5)]
#     t = tasks[0]
#     infos = t.getInfos()
#     print(infos)
