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
import math
from Location import Location, Latitude, Longitude
import simpy
from Colors import GREEN, END
import random
from Store import Store
from models import TaskMapperNet
from typing import List, TYPE_CHECKING
from CNNModel import CNNModel
from Network import LTE, LTE_PLUS

torch.set_printoptions(precision=20)

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

    nn = TaskMapperNet(input_dim=9, hidden_dim=12, output_dim=1)

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

                # Task's closest n PUs
                sorted_pu_list = Store.getClosestPUforTask(task, 5)
                TaskMapper.log(f'sorted_pu_list {sorted_pu_list}')

                # (task, pu) props batch
                tensors = [TaskMapper.taskToTensor(task, pu) for pu, _ in sorted_pu_list]
                print(tensors)
                #input()
                probas = TaskMapper.nn(torch.tensor(tensors).float())
                probas = probas.detach().numpy()

                # get index of highest proba PU
                index = np.argmax(probas)
                TaskMapper.log(f"Probas {probas.tolist()}, best index {index}")

                # sorted_pu_list contains tupples (pu, dist), ignore dist
                best_pu, _ = sorted_pu_list[index]

                # send task to best PU
                best_pu.submitTask(task)
                #input() 

            yield env.timeout(TaskMapper.CYCLE)

    def taskToTensor(task: 'Task', pu: 'ProcessingUnit') -> List[float]:
        def normalize(data, min, max):
            return (data - min)/(max - min)

        ## criticality
        crit = normalize(task.criticality.value, min=1, max=3)

        ## execution time
        # local pu execution time
        local_pu: ProcessingUnit = task.getCurrentVehicle().getPU()
        local_pu_execution_time = local_pu.getTaskExecutionTime(task)
        # remote pu execution time
        remote_pu_execution_time = pu.getTaskExecutionTime(task)

        ## offloading
        # offload time (bw, distance etc)
        
        offload_time = LTE.getTransferDuration(task.getSize())

        ## pu_queue represents PUs availabilitys based on tasks to process 
        ## and it's max queue size, range is 0, 1, 2, 3, 0 being the less available
        # Vehicle's PU task queue size (Max=100)
        #vehicle_pu_queue = normalize(local_pu.getAvailability(), 0, 3)
        # Remote PU tasks queue size (Max=100)
        #remote_pu_queue = normalize(pu.getAvailability(), 0, 3)

        ## queue
        # for now we take queue_size/max_queue_size
        vehicle_pu_queue = local_pu.getAvailability()
        remote_pu_queue = pu.getAvailability()

        ## model props
        # task.flop/pu.flops
        min, max = CNNModel.getModelFlopsMinMax()
        task_flop = normalize(task.getFlop(), min, max)
        # task.size/pu.memory
        min, max = CNNModel.getModelMemoryMinMax()
        task_size = normalize(task.getSize(), min, max)

        ## distance
        # task location
        task_location: Location = task.getCurrentVehicle().getCurrentLocation()
        task_lat, task_long = task_location.getLatitudeLongitude()
        # normalization
        task_lat = normalize(task_lat, Latitude.min, Latitude.max)
        task_long = normalize(task_long, Longitude.min, Longitude.max)

        # pu location
        pu_location: Location = pu.getParent().getLocation()
        pu_lat, pu_long = pu_location.getLatitudeLongitude()
        # normalization
        pu_lat = normalize(pu_lat, Latitude.min, Latitude.max)
        pu_long = normalize(pu_long, Longitude.min, Longitude.max)

        # task-pu distance (euclidien)
        distance = math.dist((task_lat, task_long), (pu_lat, pu_long))

        props = [crit, local_pu_execution_time, remote_pu_execution_time, 
                offload_time, vehicle_pu_queue, remote_pu_queue,
                task_flop, task_size, distance]
        return props

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