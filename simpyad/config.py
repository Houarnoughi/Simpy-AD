"""
Global variables defining the simulation
"""
import TaskMappingPolicy
import TaskSchedulingPolicy
import Networking
import Task
import ProcessingUnit
from Location import Location

# SIMULATION
SIM_STEPS = 100
ORS_TOKEN = '5b3ce3597851110001cf62480a421079db594016b4d5c12fc6980fcd'
TOWN = Location("Lille", 50.631583072533594, 3.057713469569928)
RADIUS = 2000

# VEHICLE
VEHICLE_COUNT = 1
VEHICLE_FPS = 1
VEHICLE_TASKS = [
    Task.TrafficLightDetectionTask,
    Task.TrafficSignDetectionTask,
    Task.LaneDetectionTask,
    Task.ObjectDetectionTask
]
VEHICLE_PROCESSING_UNIT = ProcessingUnit.AGX
VEHICLE_TASK_MAPPING_POLICY = TaskMappingPolicy.RandomTaskMappingPolicy
VEHICLE_TASK_SCHEDULING_POLICY = TaskSchedulingPolicy.RoundRobinSchedulingPolicy
VEHICLE_NETWORK = Networking.LTE

# RSU
RSU_COUNT = 10
RSU_EVEN_DISTRIBUTION = False
RSU_PROCESSING_UNIT = ProcessingUnit.TeslaV100
RSU_TASK_SCHEDULING_POLICY = TaskSchedulingPolicy.RoundRobinSchedulingPolicy
RSU_NETWORK = Networking.LTE_PLUS

# DATA CENTER
DATACENTER_COUNT = 99
DATACENTER_PROCESSING_UNIT = ProcessingUnit.DGXa100
DATACENTER_TASK_SCHEDULING_POLICY = TaskSchedulingPolicy.FIFOSchedulingPolicy
DATACENTER_NETWORK = Networking.LTE_PLUS


# Task offloading
OFFLOAD = True
OFFLOAD_TO_VEHICLE = False
OFFLOAD_TO_RSU = True
OFFLOAD_TO_DATACENTER = False

# Task Mapping, task to PU attribution
N_CLOSEST_PU = 2
# CustomTaskMappingPolicy #RandomTaskMappingPolicy #InplaceMappingPolicy #RandomTaskMappingPolicy
TASK_MAPPING_POLICY = TaskMappingPolicy.RandomTaskMappingPolicy
TASK_MAPPING_CALLBACK_INTERVAL = 1

MAX_TASK_COUNT = SIM_STEPS * VEHICLE_COUNT * VEHICLE_FPS * 3

# scheduler
#EDGE_TASK_SCHEDULING_POLICY = RoundRobinSchedulingPolicy
#FOG_TASK_SCHEDULING_POLICY = RoundRobinSchedulingPolicy
#CLOUD_TASK_SCHEDULING_POLICY = RoundRobinSchedulingPolicy
AGX_QUANTUM = 0.01
TESLA_QUANTUM = 0.01
DGX_QUANTUM = 0.01

# pu cicles
PU_CYCLE = 0.0001
TASK_MAPPER_CYCLE = 0.0001

# export results
OUT_FILE_PATH = f'output/results.csv'

# ui
SERVER_URL = "http://localhost:5000"
POST_TIMEOUT = 0.1
