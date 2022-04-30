"""
Global variables
"""
import os

## simulation area
MIN_LAT, MAX_LAT = 50.63089852336916, 50.650796308194764
MIN_LONG, MAX_LONG = 3.032710061899567, 3.08480585127184

# vehicle
VEHICLES = 10
FPS = 30 
N_CLOSEST_PU = 5
OFFLOAD = True
OFFLOAD_TO_VEHICLE = True
OFFLOAD_TO_RSU= True
OFFLOAD_TO_DATACENTER = False

# task mapper, task to PU attribution
RANDOM = True

# steps
SIM_TIME = 1

# scheduler
QUANTUM = 0.01

# export results
OUT_FILE_PATH = f'output/results.csv'

# Simulation Mode
DATA_GENERATION_MODE = False

