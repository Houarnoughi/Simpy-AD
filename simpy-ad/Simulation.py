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
from Colors import END
from TaskCriticality import TaskCriticality

env = simpy.Environment()

"""
Vehicle init
"""
start = Location("Gare VA", 50.36328322047431, 3.5171747551323005)
final = Location("Gare Lille", 50.63725143907785, 3.0702985651377745)
## PU init
#pu1 = AGX(task_list=[], scheduler=TaskSchedulingPolicy("FIFO"), env=env)
pu1 = AGX(task_list=[], scheduler=FIFOSchedulingPolicy(), env=env)
TaskMapper.addPU(pu1)
#pu2 = AGX(task_list=[], scheduler=TaskSchedulingPolicy("FIFO"), env=env)
#TaskMapper.addPU(pu2)

inception = CNNModel('Inception-v3', 1024)
resnet18 = CNNModel('ResNet-18', 480)
mobilenet = CNNModel('MobileNet0.25-v1', 240)

vehicle_tasks = [
    Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
    Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
    Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
]
vehicle = Vehicle(c_location=start, f_location=final, speed=10, task_list=vehicle_tasks, PU_list=[pu1], required_FPS=100, env=env)
#vehicle = Vehicle(c_location=start, f_location=final, speed=10, task_list=vehicle_tasks, PU_list=[pu2], required_FPS=1, env=env)
"""
RSU init
"""
location = Location("", 50, 45)
# PU init
#pu = TeslaV100(task_list=[], scheduler=TaskSchedulingPolicy("FIFO"), env=env)
pu = TeslaV100(task_list=[], scheduler=RoundRobinSchedulingPolicy(1), env=env)
TaskMapper.addPU(pu)

## Server init
server = Server(pu_list=[pu], bw=1, env=env)

rsu = RoadSideUnit(activity_range=100, location=location, server_list=[server], to_vehicle_bw=1, to_cloud_bw=1, env=env)

vehicle.showInfo()
rsu.showInfo()

TaskMapper.showPUs()

#input(f"{END}Enter to continue")

taskMapper = TaskMapper(env)

#print("t ", taskMapper.task_list)
#print("TaskMapper ", TaskMapper.task_list)

SIM_TIME = 10**2
print("Enter to start Simulation")
input()

env.run(until=SIM_TIME)

print("\n")
print("-------------------- Stats ----------------------")
for pu in TaskMapper.pu_list:
    pu.show_stats()
print("-------------------- Stats ----------------------")


for i, task in enumerate(TaskMapper.all_tasks):

    pu = task.getCurrentPU()
    pu_power = pu.getPower()
    task_time = task.getTotalExecutionTime()
    power = pu_power * task_time
    #print(i, task, task.isFailed(), pu, power)

for t in vehicle.all_tasks:
    #print(t, t.getTotalExecutionTime())
    pass


