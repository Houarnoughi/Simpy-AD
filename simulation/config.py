"""
Global variables defining the simulation
"""
####################################################
# SIMULATION
####################################################
SIM_STEPS = 100
ORS_TOKEN = '5b3ce3597851110001cf62480a421079db594016b4d5c12fc6980fcd'
TOWN =  ("Lille", 50.631583072533594, 3.057713469569928) #Location("Lille", 50.631583072533594, 3.057713469569928)
RADIUS = 2000

####################################################
# Vehicle
####################################################
VEHICLE_COUNT = 1
VEHICLE_FPS = 100
VEHICLE_TASKS = [
    "BehaviorPlanningTask",
    "RoutePlanningTask",
    "ControlAlgoTask",
    "TrafficLightDetectionTask",
    "TrajectoryPlanningTask",
    "MotionPredictionTask",
    "MappingTask",
    "ObjectDetectionTask",
    "ObjectTrackingTask",
    "TrafficSignDetectionTask"
]
VEHICLE_PROCESSING_UNIT = "AGX"
VEHICLE_TASK_MAPPING_POLICY = "RandomTaskMappingPolicy" #"InplaceMappingPolicy"
VEHICLE_TASK_SCHEDULING_POLICY = "RoundRobinSchedulingPolicy" #"FIFOSchedulingPolicy" #"RoundRobinSchedulingPolicy"
VEHICLE_NETWORK = "LTE"

####################################################
# RSU
####################################################
RSU_COUNT = 0
RSU_LOCATIONS = []
RSU_EVEN_DISTRIBUTION = False
RSU_PROCESSING_UNIT = "TeslaV100"
RSU_TASK_SCHEDULING_POLICY = "RoundRobinSchedulingPolicy"
RSU_NETWORK = "LTE_PLUS"

####################################################
# DATA CENTER
####################################################
DATACENTER_COUNT = 99
DATACENTER_LOCATIONS = []
DATACENTER_PROCESSING_UNIT = "DGXa100"
DATACENTER_TASK_SCHEDULING_POLICY = "FIFOSchedulingPolicy"
DATACENTER_NETWORK = "LTE_PLUS"

####################################################
# Task Offloading
####################################################
OFFLOAD = False
OFFLOAD_TO_VEHICLE = False
OFFLOAD_TO_RSU = True
OFFLOAD_TO_DATACENTER = False

####################################################
# Task Mapping
####################################################
N_CLOSEST_PU = 2
# CustomTaskMappingPolicy #RandomTaskMappingPolicy #InplaceMappingPolicy #RandomTaskMappingPolicy
TASK_MAPPING_POLICY = "RandomTaskMappingPolicy"
TASK_MAPPING_CALLBACK_INTERVAL = 1

MAX_TASK_COUNT = SIM_STEPS * VEHICLE_COUNT * VEHICLE_FPS * 3

####################################################
# Task Scheduling
####################################################
SCHEDULER_QUANTUM = 0.001
#AGX_QUANTUM = 0.01
#TESLA_QUANTUM = 0.01
#DGX_QUANTUM = 0.01

####################################################
# Processing Unit
####################################################
PU_CYCLE = 0.0001

# export results
OUT_FILE_PATH = f'output/results.csv'

####################################################
# UI
####################################################
FLASK_SERVER_PORT = 8080
FLASK_SERVER_URL = "http://localhost:5000"
POST_TIMEOUT = 0.1
