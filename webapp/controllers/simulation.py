from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config
from Location import Location
from Networking import Network
from TaskSchedulingPolicy import TaskSchedulingPolicy
from TaskMappingPolicy import TaskMappingPolicy

bp = Blueprint('simulation', __name__, url_prefix='')

global simulationThread
simulationThread = None


def getTaskMapperClass(request: dict) -> TaskMappingPolicy:
    name = request.get("mapping")
    if name == '':
        return config.TASK_MAPPING_POLICY
    else:
        from TaskMappingPolicy import UI_OPTIONS
        for option in UI_OPTIONS:
            if option.__name__ == name:
                return option


def getTaskSchedulerClass(request: dict) -> TaskSchedulingPolicy:
    name = request.get("scheduling")
    if name == '':
        return config.EDGE_TASK_SCHEDULING_POLICY
    else:
        from TaskSchedulingPolicy import UI_OPTIONS
        for option in UI_OPTIONS:
            if option.__name__ == name:
                return option


def getNetworkClass(request: dict) -> Network:
    name = request.get("networking")
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
        steps = request.json.get("steps", config.SIM_STEPS)

        vehicle: dict = request.json.get("vehicle")
        print("vehicle", vehicle)

        vehicle_count = vehicle.get("count")
        vehicle_fps = vehicle.get("fps")

        vehicle_mapping = getTaskMapperClass(vehicle)
        print("vehicle_mapping", vehicle_mapping)
        vehicle_scheduling = getTaskSchedulerClass(vehicle)
        print("vehicle_scheduling", vehicle_scheduling)
        vehicle_networking = getNetworkClass(vehicle)
        print("vehicle_networking", vehicle_networking)

        town = getTownLocation(request)
        print("town", town)
        radius = request.json.get("radius")

        # return 'start'
        simulationThread = Simulation(
            steps=int(steps),
            vehicle_count=int(vehicle_count),
            vehicle_fps=int(vehicle_fps),
            vehicle_mapping=vehicle_mapping,
            vehicle_scheduling=vehicle_scheduling,
            vehicle_networking=vehicle_networking,
            town=town,
            radius=float(radius)
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


@bp.get('/config')
def getConfig():

    data = {
        'simulation':
            {
                'steps': config.SIM_STEPS,
                'town': config.TOWN.json(),
                'radius': config.RADIUS,
                'vehicle': {
                    'count': config.VEHICLE_COUNT,
                    'fps': config.VEHICLE_FPS,
                    'mapping': config.TASK_MAPPING_POLICY.__name__,
                    'scheduling': config.EDGE_TASK_SCHEDULING_POLICY.__name__,
                    'networking': config.NETWORK.__name__
                }
            }
    }

    return data
