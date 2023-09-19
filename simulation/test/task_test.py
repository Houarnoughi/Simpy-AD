import unittest
from simulation.entity import Task, MappingTask, TrafficSignDetectionTask
from simulation.task_scheduling import RoundRobinSchedulingPolicy
from simulation.entity import ProcessingUnit, AGX
import simpy

class TaskTest(unittest.TestCase):
    def test_task_not_started(self):
        task = MappingTask()
        self.assertEqual(True, not task.isStarted())

    def test_task_started(self):
        scheduler = RoundRobinSchedulingPolicy(0.001)
        env = simpy.Environment()
        pu = AGX(scheduler=scheduler, env=env)

        task = MappingTask()

        pu.submitTask(task)

        while task.getExecutionStartTime() == -1:
            env.step()

        self.assertEqual(True, task.isStarted()) 

    def test_task_started_not_ended(self):
        scheduler = RoundRobinSchedulingPolicy(0.001)
        env = simpy.Environment()
        pu = AGX(scheduler=scheduler, env=env)

        task = MappingTask()

        pu.submitTask(task)

        while task.getExecutionStartTime() == -1 and task.getExecutionEndTime() == -1:
            env.step()

        self.assertEqual(True, task.isIncomplete()) 

    def test_task_ended(self):
        scheduler = RoundRobinSchedulingPolicy(0.001)
        env = simpy.Environment()
        pu = AGX(scheduler=scheduler, env=env)

        task = MappingTask()

        pu.submitTask(task)

        while task.getExecutionStartTime() == -1 or task.getExecutionEndTime() == -1:
            env.step()

        self.assertEqual(True, task.isFinished()) 
if __name__ == '__main__':
    unittest.main()