from abc import ABC, abstractmethod
from collections import deque
"""
Abstract class for task scheduling policy. 
Abstract methods must be implemented in a unique way
by each scheduling policy
"""
class TaskScheduling(ABC):
    def __init__(self, parallel=False) -> None:
        self.parallel=parallel
        self.task_list = []

    def getParallel(self):
        return self.parallel
    
    @abstractmethod
    def addTaskInQueue(self, task):
        """ impl by Policy """
    
    @abstractmethod
    def getNextTask(self):
        """ return task to be executed by PU """

    @abstractmethod
    def getExecutionSequence(self):
        """
        Imlplemented by chil class
        """
        
class TaskSchedulingPolicy(object):
    """
    Scheduling policies:
    - FIFO: First In First Out
    - SJF: Shortest Job First
    - TODO RoundRobin: need to implement an execution qeuegive each task a time slot (amount of flop). Decrease Task remaining FLOP.
    End when there is no more tasks in the execution qeue.
    """

    def __init__(self, preemptive=False, policy='FIFO', parallel=False):
        self.preemptive = preemptive
        self.policy = policy
        self.parallel = parallel

    def getPreemptive(self):
        return self.preemptive

    def setPreemptive(self, preemptive):
        self.preemptive = preemptive

    def getPolicy(self):
        return self.policy

    def setPolicy(self, policy):
        self.policy = policy

    def getParallel(self):
        return self.parallel

    def setParallel(self, parallel):
        self.parallel = parallel

    def getExecutionSequence(self, task_list):
        new_task_list = []

        if self.getPolicy() == 'FIFO':
            new_task_list = task_list
        if self.getPolicy() == 'SJF':
            new_task_list = sorted(task_list, key=lambda x: x.flop, reverse=False)
        return new_task_list


class FIFOSchedulingPolicy(TaskScheduling):
    def addTaskInQueue(self, task):
        task.scheduler_rounds += 1
        self.task_list.append(task)
    
    def getNextTask(self):
        if self.task_list:
            return self.task_list.pop()

    def getExecutionSequence(self):
        return self.task_list.copy()

class SJFSchedulingPolicy(TaskScheduling):
    def addTaskInQueue(self, task):
        task.scheduler_rounds += 1
        self.task_list.append(task)
    
    def getNextTask(self):
        if self.task_list:
            return self.task_list.pop()

    def getExecutionSequence(self):
        return sorted(self.task_list, key=lambda x: x.flop, reverse=False)

class RoundRobinSchedulingPolicy(TaskScheduling):
    """
    Quantum is time amount (q=10ms for example)
    Each PU will burst (q/1000)*pu.flops of Task's flops

        Task.remaining_flop -= (q/1000)*pu.flops
    
    repeated until no flops remaining
    """
    def __init__(self, quantum):
        self.quantum = quantum
        self.queue = deque()
        super().__init__()
    
    def addTaskInQueue(self, task):
        task.scheduler_rounds += 1
        self.queue.append(task)
    
    def getNextTask(self):
        if self.queue:
            return self.queue.popleft()

    def getExecutionSequence(self):
        return self.task_list
"""
fifo = FIFOSchedulingPolicy()
fifo.addTask("sec")
sjf = SJFSchedulingPolicy()

rr = RoundRobinSchedulingPolicy(10)
rr.addTask('ok')

print(fifo.task_list, sjf.task_list, rr.task_list, rr.quantum)
"""