"""
Global variables defining the simulation
"""
import os
from TaskMappingPolicy import RandomTaskMappingPolicy, InplaceMappingPolicy, CustomTaskMappingPolicy
from TaskSchedulingPolicy import RoundRobinSchedulingPolicy, FIFOSchedulingPolicy, SJFSchedulingPolicy
from Networking import LTE, LTE_PLUS
from Location import Location

## simulation area
MIN_LAT, MAX_LAT = 50.63089852336916, 50.650796308194764
MIN_LONG, MAX_LONG = 3.032710061899567, 3.08480585127184
TOWN = Location("Lille", 50.631583072533594, 3.057713469569928)
RADIUS = 2000

# vehicle
VEHICLE_COUNT = 999
VEHICLE_FPS = 30
RANDOM_MOVE = True

# rsu, 0 to 5 for this area
RSU_COUNT = 5
"""
RSU_LOCATIONS = 
addr1, 50.63725143907785, 3.0702985651377745
addr2, 50.63725143907785, 3.0702985651377745
addr3, 50.63725143907785, 3.0702985651377745
"""

# Task offloading
OFFLOAD = True
OFFLOAD_TO_VEHICLE = False
OFFLOAD_TO_RSU = True
OFFLOAD_TO_DATACENTER = False

# Task Mapping, task to PU attribution
N_CLOSEST_PU = 2
TASK_MAPPING_POLICY = RandomTaskMappingPolicy #CustomTaskMappingPolicy #RandomTaskMappingPolicy #InplaceMappingPolicy #RandomTaskMappingPolicy
TASK_MAPPING_CALLBACK_INTERVAL = 1

# steps
SIM_STEPS = 999
MAX_TASK_COUNT = SIM_STEPS * VEHICLE_COUNT * VEHICLE_FPS * 3

# scheduler
EDGE_TASK_SCHEDULING_POLICY = RoundRobinSchedulingPolicy
FOG_TASK_SCHEDULING_POLICY = RoundRobinSchedulingPolicy
CLOUD_TASK_SCHEDULING_POLICY = RoundRobinSchedulingPolicy
AGX_QUANTUM = 0.01
TESLA_QUANTUM = 0.01
DGX_QUANTUM = 0.01

# pu cicles
PU_CYCLE = 0.0001
TASK_MAPPER_CYCLE = 0.0001

# network
NETWORK = LTE

# export results
OUT_FILE_PATH = f'output/results.csv'

# ui
SERVER_URL = "http://localhost:5000"
POST_TIMEOUT = 0.1