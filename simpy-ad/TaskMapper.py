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

class TaskMapper:

    pu_list = []
    task_list = []

    success_task_list = []
    failed_task_list = []
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
    output_dim = 2
    nn = nn.Sequential(
        nn.Linear(input_dim, 16, bias=True),
        nn.ReLU(),
        nn.Linear(16, 16, bias=True), 
        nn.ReLU(),
        nn.Linear(16, output_dim, bias=True),
        nn.Softmax()
    )

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
                self.log(f"[TaskMapper] task count {len(TaskMapper.task_list)}")
                # FIFO
                task = TaskMapper.task_list.pop(0)
                # GET PU
                pu = random.choice(TaskMapper.pu_list)

                self.log(f"[TaskMapper] submit task {task.name} to {pu} at {env.now}")
                pu.submitTask(task)

                """
                n = len(TaskMapper.pu_list)
                index = random.choice(range(n))
                
                self.log(f"[TaskMapper] submit task {task.name} to {TaskMapper.pu_list[index]} at {env.now}")
                TaskMapper.pu_list[index].submitTask(task)
                """

            yield env.timeout(1)

    # called on runtime
    def addTask(task):
        TaskMapper.task_list.append(task)

    def addPU(pu):
        TaskMapper.pu_list.append(pu)

    def removeTask(task):
        TaskMapper.task_list.remove(task)

    def log(self, message):
        print(f"{GREEN}{message}{END}")
    
    def showTasks():
        print(f"{GREEN}[TaskMapper] Tasks {TaskMapper.task_list} {END}")

    def showPUs():
        print(f"{GREEN}[TaskMapper] PUs {TaskMapper.pu_list} {END}")
    
    def distance(self, l1: Location, l2: Location):
        return np.sqrt( 
            ((l2.latitude-l1.latitude)**2) + 
            ((l2.longitude-l1.longitude)**2) 
        )

    def getClosestPUforTask(self, task):
        t = (10,5)
        
    def assignTaskToPu(self):
        pass

    def optimize(self):
        pass
        
#scheduler = TaskSchedulingPolicy('FIFO')
#t = TaskMapper(scheduler=scheduler)

#t = (10,5)
#points = [(5,12), (3,0), (1,2), (9,3), (5, 14)]

#points.sort(key=lambda p: np.sqrt( ((t[0] - p[0])**2) + ((t[1] - p[1])**2) ) )
#print(points)