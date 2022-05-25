from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config
from Location import Location

bp = Blueprint('simulation', __name__, url_prefix='')

global simulationThread
simulationThread = None

def getTaskMapperClass(request):
    name = request.json.get("vehicle_mapping")
    if name == '':
        return config.TASK_MAPPING_POLICY
    else:
        from TaskMappingPolicy import UI_OPTIONS
        for option in UI_OPTIONS:
            if option.__name__ == name:
                return option

def getTaskSchedulerClass(request):
    name = request.json.get("vehicle_scheduling")
    if name == '':
        return config.EDGE_TASK_SCHEDULING_POLICY
    else:
        from TaskSchedulingPolicy import UI_OPTIONS
        for option in UI_OPTIONS:
            if option.__name__ == name:
                return option

def getNetworkClass(request):
    name = request.json.get("vehicle_networking")
    if name == '':
        return config.NETWORK
    else:
        from Networking import UI_OPTIONS
        for option in UI_OPTIONS:
            if option.__name__ == name:
                return option

def getTownLocation(request) -> Location:
    town = request.json.get("town")
    return Location("", town['latitude'], town['longitude'])

@bp.post('/start')
def startSimulation():
    try:
        global simulationThread

        if simulationThread:
            print("already running a simu, please stop it first")
            return "already running a simu, please stop it first"
        
        print(request.json)
        steps = request.json.get("steps", config.SIM_TIME)
        vehicle_count = request.json.get("vehicle_count", config.VEHICLE_COUNT)
        vehicle_fps = request.json.get("vehicle_fps", config.FPS)
        
        vehicle_mapping = getTaskMapperClass(request)
        print("vehicle_mapping", vehicle_mapping)
        vehicle_scheduling = getTaskSchedulerClass(request)
        print("vehicle_scheduling", vehicle_scheduling)
        vehicle_networking = getNetworkClass(request)
        print("vehicle_networking", vehicle_networking)

        town = getTownLocation(request)
        print("town", town)
        area_range = request.json.get("area_range", config.SIM_TIME)

        #return 'start'
        simulationThread = Simulation(
            steps=int(steps), 
            vehicle_count=int(vehicle_count), 
            vehicle_fps=int(vehicle_fps),
            vehicle_mapping=vehicle_mapping,
            vehicle_scheduling=vehicle_scheduling,
            vehicle_networking=vehicle_networking,
            town=town,
            area_range=float(area_range)
        )
        simulationThread.start()

        return "started"
    except Exception as e:
        print("app.startSimulation ", e)
        return "error"

@bp.post('/stop')
def stopSimulation():
    print("stopping simulation")
    global simulationThread
    try:
        simulationThread.stop()
        simulationThread = None

        Store.clear()

        return "stopped"
    except Exception as e:
        print(e)
        return "error"