"""
Simulation scenario

    Vehicle - 1x
        PU - TX2 x1
    
    RSU - 1x
        Server - 1x
            PU - TeslaV100 1x
    
    TaskMapper - 1x
        Task - n
        PU - 2

    Trip
        Gare VA -> Gare Lille
        Frames -> 189639
    
    Goal is 60 FPS, repeat trip until FPS reaches 60 by optimizing model
    or until required latency is reached (or almost) 
"""
import simpy
from Vehicle import Vehicle
from Location import Location
from ProcessingUnit import AGX, TeslaV100
from TaskSchedulingPolicy import RoundRobinSchedulingPolicy, FIFOSchedulingPolicy
from RoadSideUnit import RoadSideUnit
from Server import Server
from CNNModel import CNNModel
from Task import Task
from TaskMapper import TaskMapper
from Colors import END, GREEN, YELLOW, RED, BLUE
from TaskCriticality import TaskCriticality
from Store import Store
from Plotter import Plotter
import config
import os
import random

env = simpy.Environment()

"""
vehicle task types
"""
inception = CNNModel('Inception-v3', 1024)
resnet18 = CNNModel('ResNet-18', 480)
mobilenet = CNNModel('MobileNet0.25-v1', 240)

vehicle_tasks = [
    Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
    Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
    Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
    Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
    Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
    Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
]
"""
Vehicle init

Lille triangle limits

50.650796308194764, 3.037816505423616 - 50.649129252863915, 3.0776296527024805
50.63089852336916, 3.032710061899567 - 50.631246374330935, 3.08480585127184
"""

for _ in range(config.VEHICLE_COUNT):
    ## PU init
    pu1 = AGX(task_list=[], scheduler=RoundRobinSchedulingPolicy(config.AGX_QUANTUM), env=env)
    Store.addPU(pu1)

    vehicle = Vehicle(
        c_location=Location("random", random.uniform(config.MIN_LAT, config.MAX_LAT), random.uniform(config.MIN_LONG, config.MAX_LONG)), 
        f_location=Location("Gare Lille", 50.63725143907785, 3.0702985651377745), 
        speed=10, 
        bw = 10e6,
        task_list=vehicle_tasks, 
        PU_list=[pu1], 
        required_FPS=config.FPS, 
        env=env)
    vehicle.showInfo()
    Store.vehicle_list.append(vehicle)
"""
RSU init  x5
"""
locations = [
    Location("Zoo de Lille", 50.64099393427632, 3.044548801247785),
    Location("Jardin des Géants", 50.64347018158827, 3.0806523044990617),
    Location("Palais bx arts", 50.63222755233801, 3.0628195821035655),
    Location("Moulins", 50.620905648844506, 3.06973893974428),
    Location("wazemmes", 50.627218409442975, 3.0400339217074266)
]
for i in range(config.RSU_COUNT):
    pu = TeslaV100(task_list=[], scheduler=RoundRobinSchedulingPolicy(config.TESLA_QUANTUM), env=env)
    Store.addPU(pu)

    rsu = RoadSideUnit(
        activity_range=100, 
        location=locations[i], 
        server_list=[
            Server(pu_list=[pu], bw=1, env=env)
        ], 
        to_vehicle_bw=1, to_cloud_bw=1, env=env)
    rsu.showInfo()
    Store.rsu_list.append(rsu)

Store.showPUs()

taskMapper = TaskMapper(env)

print("Enter to start Simulation")
input()

p = Plotter(env)

env.run(until=config.SIM_TIME)

Store.showStats()
Store.export()

# task: Task = None
# for task in Store.all_tasks:
#     print(task.id, task.execution_start_time, task.execution_end_time, task.remaining_flop)