from abc import ABC, abstractmethod
from collections import deque
from Exceptions import NoMoreTasksException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Task import Task
"""
Abstract class for task scheduling policy. 
Abstract methods must be implemented in a unique way
by each scheduling policy
"""
class TaskSchedulingPolicy(ABC):
    def __init__(self, parallel=False) -> None:
        self.parallel=parallel
        self.task_list = []
        self.quantum = None

    def getParallel(self):
        return self.parallel
    
    def toJSON(self):
        return 'manu'
    
    @abstractmethod
    def addTaskInQueue(self, task: 'Task'):
        """ impl by Policy """
    
    @abstractmethod
    def getNextTask(self) -> 'Task':
        """ return task to be executed by PU """

    @abstractmethod
    def getQueueSize(self) -> int:
        """ return number of tasks in the queue """    

    @abstractmethod
    def getQuantum(self) -> float:
        """ return number of tasks in the queue """  

class FIFOSchedulingPolicy(TaskSchedulingPolicy):
    def addTaskInQueue(self, task):
        task.scheduler_rounds += 1
        self.task_list.append(task)
    
    def getNextTask(self) -> 'Task':
        if self.task_list:
            return self.task_list.pop()
        else:
            raise NoMoreTasksException()
    
    def getQueueSize(self) -> int:
        return len(self.task_list)
    
    def getQuantum(self) -> float:
        return None

class SJFSchedulingPolicy(TaskSchedulingPolicy):
    def addTaskInQueue(self, task: 'Task'):
        task.scheduler_rounds += 1
        self.task_list.append(task)
    
    def getNextTask(self) -> 'Task':
        if self.task_list:
            return self.task_list.pop()
        else:
            raise NoMoreTasksException()

    def getQueueSize(self) -> int:
        return len(self.task_list)
    
    def getQuantum(self) -> float:
        return None

class RoundRobinSchedulingPolicy(TaskSchedulingPolicy):
    """
    Quantum is time amount (q=10ms for example)
    Each PU will burst (q/1000)*pu.flops of Task's flops

        Task.remaining_flop -= (q/1000)*pu.flops
    
    repeated until no flops remaining
    """
    def __init__(self, quantum: float):
        super().__init__()
        self.quantum: float = quantum
        self.queue = deque()
    
    def addTaskInQueue(self, task: 'Task'):
        self.queue.append(task)
    
    def getNextTask(self) -> 'Task':
        if self.queue:
            return self.queue.popleft()
        else:
            raise NoMoreTasksException()

    def getQueueSize(self) -> int:
        return len(self.queue)
    
    def getQuantum(self) -> float:
        return self.quantum

UI_OPTIONS = [
    FIFOSchedulingPolicy,
    SJFSchedulingPolicy,
    RoundRobinSchedulingPolicy
]

if __name__ == '__main__':
    
    fifo = FIFOSchedulingPolicy()
    fifo.addTaskInQueue("sec")
    sjf = SJFSchedulingPolicy()

    rr = RoundRobinSchedulingPolicy(10)
    rr.addTaskInQueue('ok')

    print(fifo.task_list, sjf.task_list, rr.task_list, rr.quantum)
    