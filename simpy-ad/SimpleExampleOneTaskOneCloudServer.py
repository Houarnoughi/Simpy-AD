from Task import Task
from ProcessingUnit import DGXa100
from Server import Server
from CNNModel import CNNModel
from TaskSchedulingPolicy import TaskSchedulingPolicy
import simpy


def main():
    # First, we create a simulation environment
    env = simpy.Environment()

    # Create the list of the tasks to be submitted to the Processing Unit
    FLOPS_task_list = []

    # Create a PU list to be added to the server
    PU_list = []

    # Create an instance of a Deep Learning task. A CNN
    resnet200 = CNNModel('ResNet-200', 1792)
    max_flops_task = Task(resnet200.getModelFLOPS(), resnet200.getModelMemory())
    FLOPS_task_list.append(max_flops_task)

    xception = CNNModel('Xception', 480)
    max1_flops_task = Task(xception.getModelFLOPS(), xception.getModelMemory())
    FLOPS_task_list.append(max1_flops_task)

    inception = CNNModel('Inception-v3', 256)
    mid_flops_task = Task(inception.getModelFLOPS(), inception.getModelMemory())
    FLOPS_task_list.append(mid_flops_task)

    dpn92 = CNNModel('DPN-92', 64)
    min1_mem_task = Task(dpn92.getModelFLOPS(), dpn92.getModelMemory())
    FLOPS_task_list.append(min1_mem_task)

    mnasnet = CNNModel('MNASNet0.35', 32)
    min_flops_task = Task(mnasnet.getModelFLOPS(), mnasnet.getModelMemory())
    FLOPS_task_list.append(min_flops_task)

    # Tasks sorted by Memory requirements
    memory_task = []
    dpn107 = CNNModel('DPN-107', 896)
    max_mem_task = Task(dpn107.getModelFLOPS(), dpn107.getModelMemory())
    memory_task.append(max_mem_task)

    inception = CNNModel('Inception-v3', 1024)
    max1_mem_task = Task(inception.getModelFLOPS(), inception.getModelMemory())
    memory_task.append(max1_mem_task)

    resnet18 = CNNModel('ResNet-18', 480)
    mid_mem_task = Task(resnet18.getModelFLOPS(), resnet18.getModelMemory())
    memory_task.append(mid_mem_task)

    resnet200 = CNNModel('ResNet-200', 568)
    mid1_mem_task = Task(resnet200.getModelFLOPS(), resnet200.getModelMemory())
    memory_task.append(mid1_mem_task)

    mobilenet = CNNModel('MobileNet0.25-v1', 240)
    min_mem_task = Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory())
    memory_task.append(min_mem_task)

    scheduler = TaskSchedulingPolicy(preemptive=False, policy='FIFO', parallel=True)
    tesla = DGXa100(FLOPS_task_list, scheduler, env)
    PU_list.append(tesla)

    server = Server(PU_list, 100, env)
    env.run()

    for task in FLOPS_task_list:
        tmps = task.getTotalExecutionTime() / 1000
        offloading_time = (task.getSize() / (server.getBandwidth() / 8)) + (task.getSize() / ((server.getBandwidth()*100) / 8))
        total = tmps + offloading_time
        power = task.getCurrentPU().getPower()
        print(f'Total execution time for {task.getTaskName()} is {total}')
        print(f'Total energy consumed by for {task.getTaskName()} is {tmps * power}')


if __name__ == "__main__":
    main()
