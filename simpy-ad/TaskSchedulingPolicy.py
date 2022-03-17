from abc import ABC, abstractmethod

"""
Abstract class for task scheduling policy. 
Abstract methods must be implemented in a unique way
by each scheduling policy
"""
class TaskScheduling(ABC):
    @abstractmethod
    def getExecutionSequence(self, task_list):
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
    def getExecutionSequence(task_list):
        return task_list.copy()

class SJFSchedulingPolicy(TaskScheduling):
    def getExecutionSequence(task_list):
        return sorted(task_list, key=lambda x: x.flop, reverse=False)

class RoundRobinSchedulingPolicy(TaskScheduling):
    pass

#fifo = FIFOSchedulingPolicy()
#sjf = SJFSchedulingPolicy()