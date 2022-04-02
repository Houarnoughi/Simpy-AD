"""
Task Mapper 
    - keeps refs of every Processing Unit in the simulation context
    - has refs to every task at runtime

    - stores processed Tasks, completed or failed for later stats

We can access their location via 
    - Task: 
        Task.getCurrentVehicle().getCurrentLocation()
    - Vehicle PU: 
        (AGX, TX2).getCurrentVehicle().getCurrentLocation()
    - RSU PU:
        (TeslaV100).getCurrentServer().getParent().getCurrentLocation()
    - DataCenter PU:
        (DGXa100).getCurrentServer().getParent().getCurrentLocation()

    RSU -> Cloud is fastest

    t1, t2, t3
    pu1, pu2, pu3, pu4, pu5

    t3, 
"""
from torch import nn
import torch
from TaskSchedulingPolicy import TaskSchedulingPolicy
import numpy as np
from Location import Location
import simpy
from Colors import GREEN, END
import random
from Store import Store
from models import TaskMapperNet
from typing import List, TYPE_CHECKING
from CNNModel import CNNModel

if TYPE_CHECKING:
    from ProcessingUnit import ProcessingUnit
    from Task import Task

class TaskMapper:

    CYCLE = 0.001
    pu_list = []
    task_list = []

    success_task_list = []
    failed_task_list = []
    all_tasks = []

    nn = TaskMapperNet(input_dim=10, hidden_dim=12, output_dim=1)

    def __init__(self, env):
        self.env = env
        self.process = env.process(self.work(env))
    
    def work(self, env):
        while True:
            if not Store.task_list:
                yield env.timeout(0)
            else:
                Store.log(f"task count {Store.getTaskCount()}")
                
                # FIFO
                task: Task = Store.getTask()

                sorted_pu_list = Store.getClosestPUforTask(task, 5)
                print('sorted_pu_list', sorted_pu_list)

                # GET Random PU
                pu: ProcessingUnit = Store.getRandomPU()

                # Tensor of a Task's normalized props
                taskTensor = TaskMapper.taskToTensor(task, pu)
                print(taskTensor)
                input()

                # distance
                task_location = task.getCurrentVehicle().getLocation()
                pu_location = pu.getParent().getLocation()
                d = Location.getDistanceInMeters(task_location, pu_location)
                #print(task_location, pu_location, d)

                # send task to PU
                pu.submitTask(task)

            yield env.timeout(TaskMapper.CYCLE)

    def taskToTensor(task: 'Task', pu: 'ProcessingUnit') -> torch.Tensor:
        def normalize(data, min, max):
            return (data - min)/(max - min)
        # criticality
        crit = normalize(task.criticality.value, min=1, max=3)
        # local pu execution time
        local_pu: ProcessingUnit = task.getCurrentVehicle().getPU()
        local_pu_execution_time = local_pu.getTaskExecutionTime(task)
        # remote pu execution time
        remote_pu_execution_time = pu.getTaskExecutionTime(task)
        # offload time (bw, distance etc)
        offload_time = 0
        ## pu_queue represents PUs availabilitys based on tasks to process 
        ## and it's max queue size, range is 0, 1, 2, 3, 0 being the less available
        # Vehicle's PU task queue size (Max=100)
        #vehicle_pu_queue = normalize(local_pu.getAvailability(), 0, 3)
        # Remote PU tasks queue size (Max=100)
        #remote_pu_queue = normalize(pu.getAvailability(), 0, 3)

        # for now we take queue_size/max_queue_size
        vehicle_pu_queue = local_pu.getAvailability()
        remote_pu_queue = pu.getAvailability()

        # task.flop/pu.flops
        min, max = CNNModel.getModelFlopsMinMax()
        task_flop = normalize(task.getFlop(), min, max)

        # task.size/pu.memory
        min, max = CNNModel.getModelMemoryMinMax()
        task_size = normalize(task.getSize(), min, max)

        return [crit, local_pu_execution_time, remote_pu_execution_time, 
                offload_time, vehicle_pu_queue, remote_pu_queue,
                task_flop, task_size]

    def log(message):
        print(f"{GREEN}[TaskMapper] {message}{END}")
    
    def showTasks():
        TaskMapper.log(f"Tasks {TaskMapper.task_list}")

    def showPUs():
        TaskMapper.log(f"PUs {TaskMapper.pu_list}")

    # returns a list of sorted n closest PUs to a Task (Vehicle) 
    def getClosestPUforTask(task, n) -> List['ProcessingUnit']:
        task_location: Location = task.getCurrentVehicle().getLocation()
        #pu_distance_list = [(pu, Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())) for pu in TaskMapper.pu_list]
        pu_distance_list = []

        pu: ProcessingUnit = None
        for pu in TaskMapper.pu_list:
            dist = Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())
            item = (pu, dist)
            pu_distance_list.append(item)

        return sorted(pu_distance_list, key=lambda item: item[1])[:n]
        
    def assignTaskToPu(self):
        pass

    def optimize():
        TaskMapper.log('Training todo')
        pass