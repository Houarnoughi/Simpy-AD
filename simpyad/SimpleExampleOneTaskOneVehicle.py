from Task import Task
from ProcessingUnit import AGX, TX2
from Vehicle import Vehicle
from CNNModel import CNNModel
from Location import Location
from TaskSchedulingPolicy import TaskSchedulingPolicy
import simpy
import Units


def main():
    # First, we create a simulation environment
    env = simpy.Environment()

    # Create source and destination locations
    src = Location('92T rue roger Salengro, 59300 Famars', 50.319860, 3.518210)
    dst = Location('Place d"armes 59300, Valenciennes', 50.357760, 3.523180)
    print('The distance between "{0}" and "{1}" is {2} Km'.format(src.getAddress(), dst.getAddress(),
                                                                  src.getDistanceInKm(dst)))
    # Create the list of the tasks to be submitted to the Processing Unit
    FLOPS_task_list = []
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

    # Create a PU list to be added to the server
    PU_list = []

    scheduler = TaskSchedulingPolicy(preemptive=False, policy='FIFO', parallel=True)
    agx1 = AGX(memory_task, scheduler, env)
    PU_list.append(agx1)
    # tx2 = TX2(task_list, scheduler, env)
    # PU_list.append(tx2)

    vehicle = Vehicle(src, dst, 30, FLOPS_task_list, PU_list, 30, env)
    print(vehicle.getFramesToBeProcessed(), ' Frames to process')

    # env.run()

    for task in memory_task:
        tmps = task.getTotalExecutionTime() / 1000
        power = task.getCurrentPU().getPower()
        print("Flops", task.getFlop()/Units.Units.giga)
        print("Memory", task.getSize())
        print('Total execution time fot {0} is {1}'.format(task.getTaskName(), tmps))
        print('Total energy consumed by for {0} is {1}'.format(task.getTaskName(), tmps * power))


if __name__ == "__main__":
    main()
