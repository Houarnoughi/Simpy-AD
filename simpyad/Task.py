from typing import TYPE_CHECKING
from enum import Enum
from abc import ABC, abstractmethod
from CNNModel import AlexNet

if TYPE_CHECKING:
    from Vehicle import Vehicle
    from ProcessingUnit import ProcessingUnit

class TaskCriticality(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

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


class Task(ABC):
    """
    Abstract class for defining tasks

    Task 
        - is created on a vehicle
        - is assigned (by TaskMappingPolicy) to a PU to be executed
        - flop is the amount of computation
        - remaining_flop is the amount to execute, modified by PU
        - size is task's memory footprint
        - execution_start_time is Simpy time of when PU started executing the task
        - execution_end_time is Simpy time set when there's no more remaining_flop to execute
        - scheduler_rounds is the number of times a task's been through the TaskScheduler (Round Robin)
    """
    idx = 1

    def __init__(self, flop: float, size: float, criticality: TaskCriticality):
        self.id = Task.idx
        self.name = f'Task-{self.id}'
        Task.idx += 1

        # parent
        self.vehicle: 'Vehicle' = None

        self.status: TaskStatus = None
        self.pu: 'ProcessingUnit' = None

        # props
        self.flop: float = flop
        self.remaining_flop: float = flop
        self.size: float = size
        self.criticality: TaskCriticality = criticality

        # execution
        self.deadline: float = 0
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

    def setRemainingFlop(self, remaining_flop: float):
        self.remaining_flop = remaining_flop

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
        return f'[{self.name}: {self.__class__.__name__}, flop={self.flop}, remainingFlop={self.remaining_flop}, size={self.size}, startTime={self.execution_start_time}, endTime={self.execution_end_time}, pu={self.pu}, vehicle={self.vehicle}, status={self.status}, rounds={self.scheduler_rounds}]'

    def __repr__(self) -> str:
        return f'[{self.name}, pu={self.pu}]'


class TrafficSignDetectionTask(Task):
    FLOP = 2300
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class LaneDetectionTask(Task):
    FLOP = 230
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class ObjectDetectionTask(Task):
    FLOP = 2300000000
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class ObjectTrackingTask(Task):
    FLOP = 230
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class MappingTask(Task):
    FLOP = 230
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class LocalizationAlgoTask(Task):
    FLOP = 230
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class MotionPredictionTask(Task):
    FLOP = 230
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class TrajectoryPlanningTask(Task):
    FLOP = 230
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

class BehaviorPlanningTask(Task):
    FLOP = 100_000_000_000
    SIZE = 2100
    CRITICALITY = TaskCriticality.MEDIUM

    def __init__(self):
        super().__init__(
            flop=self.FLOP,
            size=self.SIZE,
            criticality=self.CRITICALITY
        )

class RoutePlanningTask(Task):
    FLOP = 50_000_000_000
    SIZE = 2200
    CRITICALITY = TaskCriticality.MEDIUM

    def __init__(self):
        super().__init__(
            flop=self.FLOP,
            size=self.SIZE,
            criticality=self.CRITICALITY
        )

class ControlAlgoTask(Task):
    FLOP = 100_000_000_000
    SIZE = 200
    CRITICALITY = TaskCriticality.MEDIUM

    def __init__(self):
        super().__init__(
            flop=self.FLOP,
            size=self.SIZE,
            criticality=self.CRITICALITY
        )

class TrafficLightDetectionTask(Task):
    
    MODEL = AlexNet()

    FLOP = 40_000_000_000
    SIZE = 100
    CRITICALITY = TaskCriticality.HIGH
    
    def __init__(self):
        super().__init__(
            flop=self.FLOP,
            size=self.SIZE,
            criticality=self.CRITICALITY
        )
    

UI_OPTIONS = [
    TrafficLightDetectionTask,
    TrafficSignDetectionTask,
    LaneDetectionTask,
    ObjectDetectionTask,
    ObjectTrackingTask,
    MappingTask,
    LocalizationAlgoTask,
    MotionPredictionTask,
    TrajectoryPlanningTask,
    BehaviorPlanningTask,
    RoutePlanningTask,
    ControlAlgoTask
]

def getTasks(request: dict) -> list[Task]:
    selected_task_list = request.get("tasks")

    return [option for option in UI_OPTIONS if option.__name__ in selected_task_list]

   

if __name__ == '__main__':

    t1 = TrafficLightDetectionTask()
    t2 = ControlAlgoTask()

    print(t1.getInfos())
    print(t2.getInfos())
    
    print()
    
    t1.decreaseRemainingFlop(50)
    t2.decreaseRemainingFlop(300)

    print(t1.getInfos())
    print(t2.getInfos())
