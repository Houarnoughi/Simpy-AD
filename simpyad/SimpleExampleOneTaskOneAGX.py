from Task import Task
from ProcessingUnit import AGX, TX2
from CNNModel import CNNModel
from TaskSchedulingPolicy import TaskSchedulingPolicy
import simpy


def main():
    # First, we create a simulation environment
    env = simpy.Environment()

    # Create the list of the tasks to be submitted to the Processing Unit
    task_list = []

    # Create an instance of a Deep Learning task. A CNN
    densenet = CNNModel('DenseNet-121', 1024)
    task1 = Task(densenet.getModelFLOPS(), densenet.getModelMemory())
    task_list.append(task1)

    dpn = CNNModel('DPN-107', 896)
    task2 = Task(dpn.getModelFLOPS(), dpn.getModelMemory())
    task_list.append(task2)

    inception = CNNModel('Inception-v3', 1024)
    task3 = Task(inception.getModelFLOPS(), inception.getModelMemory())

    # The task scheduler
    scheduler = TaskSchedulingPolicy(preemptive=False, policy='SJF', parallel=True)
    agx1 = AGX([task1, task2, task3], scheduler, env)
    # tx2 = TX2([task3], env)
    # print('Execution time on tx2 %d' % tx2.getTaskExecutionTime(task3))

    env.run()


if __name__ == "__main__":
    main()
