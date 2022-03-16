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
from models import TaskMapperNet

class TaskMapper:

    pu_list = []
    task_list = []

    success_task_list = []
    failed_task_list = []
    all_tasks = []
    # env = None

    """
    min-max location
    
    model input -> Task props, PU props, bandwidth, distance

    Task -> 
        input -> (offloading_time or total), -flop-, size, euclid(task, pu), execution_timejen, bwToEdge, bwToFog
        
        offloading_time = task.getSize() / (server.getBandwidth()/8)
        total = task.getTotalExecutionTime() / 1000 + offloading_time

          output -> assing to a PU 
    """
    input_dim = 9

    nn = TaskMapperNet(input_dim=10, hidden_dim=input_dim*2)

    def __init__(self, env):
        self.env = env
        #Thread(target=self.work, args=(env,)).start()
        self.process = env.process(self.work(env))
    
    def work(self, env):
        while True:
            #print("TaskMapper: work")
            if len(TaskMapper.task_list) == 0:
                pass
            else:
                #TaskMapper.showTasks()
                TaskMapper.log(f"task count {len(TaskMapper.task_list)}")
                # FIFO
                task = TaskMapper.task_list.pop(0)
                # GET PU
                pu = random.choice(TaskMapper.pu_list)

                TaskMapper.log(f"submit task {task.name} to {pu} at {env.now}")
                # send task to PU
                pu.submitTask(task)


            yield env.timeout(1)

    # called on runtime
    def addTask(task):
        TaskMapper.task_list.append(task)

    def addPU(pu):
        TaskMapper.pu_list.append(pu)

    def removeTask(task):
        TaskMapper.task_list.remove(task)

    def log(message):
        print(f"{GREEN}[TaskMapper] {message}{END}")
    
    def showTasks():
        TaskMapper.log(f"Tasks {TaskMapper.task_list}")

    def showPUs():
        TaskMapper.log(f"PUs {TaskMapper.pu_list}")
    
    def distance(self, l1: Location, l2: Location):
        return np.sqrt( 
            ((l2.latitude-l1.latitude)**2) + 
            ((l2.longitude-l1.longitude)**2) 
        )

    def getClosestPUforTask(self, task):
        t = (10,5)
        
    def assignTaskToPu(self):
        pass

    def optimize():
        TaskMapper.log('Training todo')
        pass
        
#scheduler = TaskSchedulingPolicy('FIFO')
#t = TaskMapper(scheduler=scheduler)

#t = (10,5)
#points = [(5,12), (3,0), (1,2), (9,3), (5, 14)]

#points.sort(key=lambda p: np.sqrt( ((t[0] - p[0])**2) + ((t[1] - p[1])**2) ) )
#print(points)