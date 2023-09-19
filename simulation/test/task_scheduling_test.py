import unittest
import sys
import os
import simpy
import math
from simulation.entity import Task, MappingTask, TrafficSignDetectionTask
from simulation.task_scheduling import TaskSchedulingPolicy
from simulation.task_scheduling import FIFOSchedulingPolicy
from simulation.task_scheduling import SJFSchedulingPolicy
from simulation.task_scheduling import RoundRobinSchedulingPolicy
from simulation.entity import ProcessingUnit, AGX

class FIFOTest(unittest.TestCase):
    def test_task_queue(self):
        scheduler: TaskSchedulingPolicy = FIFOSchedulingPolicy()
        task: Task = MappingTask()

        scheduler.addTaskInQueue(task)
        task = scheduler.getNextTask()
        scheduler.addTaskInQueue(task)

        self.assertEqual(task.getSchedulerRounds(), 2)

class SJFTest(unittest.TestCase):
    def test_shortest_task(self):
        scheduler: TaskSchedulingPolicy = SJFSchedulingPolicy()

        slow_task: Task = MappingTask()
        fast_task: Task = TrafficSignDetectionTask()

        scheduler.addTaskInQueue(slow_task)
        scheduler.addTaskInQueue(fast_task)

        task = scheduler.getNextTask()

        #print(slow_task, fast_task, task)

        self.assertEqual(task.id, slow_task.id)

class RoundRobinSchedulingPolicyTest(unittest.TestCase):
    def test_sched_rounds(self):
        scheduler = RoundRobinSchedulingPolicy(0.001)
        env = simpy.Environment()
        pu: ProcessingUnit = AGX(scheduler=scheduler, env=env)

        task: Task = TrafficSignDetectionTask()

        BURNST = pu.getQuantumFlop()
        NEEDED_ROUNDS = math.ceil( task.getFlop()/BURNST )
        print("NEEDED_ROUNDS: ", NEEDED_ROUNDS)

        pu.submitTask(task)
        print(task)

        print(task)

        # run simulation until task is executed
        while task.getExecutionEndTime() == -1:
            print("task: ", task)
            env.step()

        print(task)
        self.assertEqual(NEEDED_ROUNDS, task.getSchedulerRounds())

"""
class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
"""
if __name__ == '__main__':
    unittest.main()