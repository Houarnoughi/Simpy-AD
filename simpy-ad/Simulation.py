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
from Colors import END, GREEN, YELLOW, RED
from TaskCriticality import TaskCriticality
from Store import Store

env = simpy.Environment()

"""
Vehicle init
"""
start = Location("Gare VA", 50.36328322047431, 3.5171747551323005)
final = Location("Gare Lille", 50.63725143907785, 3.0702985651377745)
## PU init
pu1 = AGX(task_list=[], scheduler=RoundRobinSchedulingPolicy(0.005), env=env)
Store.addPU(pu1)

inception = CNNModel('Inception-v3', 1024)
resnet18 = CNNModel('ResNet-18', 480)
mobilenet = CNNModel('MobileNet0.25-v1', 240)

vehicle_tasks = [
    Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
    Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
    Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
]
vehicle = Vehicle(
    c_location=start, 
    f_location=final, 
    speed=10, 
    bw = 10e6,
    task_list=vehicle_tasks, PU_list=[pu1], required_FPS=30, env=env)
"""
RSU init
"""
location = Location("", 50, 45)
# PU init
pu2 = TeslaV100(task_list=[], scheduler=RoundRobinSchedulingPolicy(10), env=env)
Store.addPU(pu2)

## Server init
server = Server(pu_list=[pu2], bw=1, env=env)

rsu = RoadSideUnit(activity_range=100, location=location, server_list=[server], to_vehicle_bw=1, to_cloud_bw=1, env=env)

vehicle.showInfo()
rsu.showInfo()

Store.showPUs()

taskMapper = TaskMapper(env)

SIM_TIME = 10**0
print("Enter to start Simulation")
input()

env.run(until=SIM_TIME)

print("\n")
print("-------------------- Stats ----------------------")
for pu in TaskMapper.pu_list:
    pu.show_stats()

# success
print(f'{GREEN}Success tasks')
t: Task = None
ended_lambda = lambda t: t.execution_start_time != -1 and t.execution_end_time != -1
for t in list(filter(ended_lambda, Store.all_tasks)):
    pass
    print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop')

print(f'{YELLOW}Not complete tasks')
started_not_ended_lambda = lambda t: t.execution_start_time != -1 and t.execution_end_time == -1
for t in list(filter(started_not_ended_lambda, Store.all_tasks)):
    pass
    print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop')

print(f'{RED}Not started tasks')
not_started_lambda = lambda t: t.execution_start_time == -1 and t.execution_end_time == -1
for t in list(filter(not_started_lambda, Store.all_tasks)):
    pass
    print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop')

print(f"{YELLOW}-------------------- Stats ----------------------")