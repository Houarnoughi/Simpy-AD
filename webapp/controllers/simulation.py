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
        return config.VEHICLE_TASK_MAPPING_POLICY
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
        # Simulation
        steps = request.json.get("steps", config.SIM_STEPS)
        radius = request.json.get("radius")
        town = getTownLocation(request)
        print("town", town)

        # Vehicle
        vehicle: dict = request.json.get("vehicle")
        vehicle_count = vehicle.get("count")
        vehicle_fps = vehicle.get("fps")
        vehicle_mapping = getTaskMapperClass(vehicle)
        vehicle_scheduling = getTaskSchedulerClass(vehicle)
        vehicle_networking = getNetworkClass(vehicle)
        print("VEHICLE", vehicle_count, vehicle_fps, vehicle_mapping, vehicle_scheduling, vehicle_networking)

        # RSU
        rsu: dict = request.json.get("rsu")
        rsu_count = rsu.get("count")
        rsu_scheduling = getTaskSchedulerClass(rsu)
        rsu_network = getNetworkClass(rsu)
        print("RSU", rsu_count, rsu_scheduling, rsu_network)

        # DATACENTER
        datacenter: dict = request.json.get("datacenter")
        datacenter_count = datacenter.get("count")
        datacenter_scheduling = getTaskSchedulerClass(datacenter)
        datacenter_network = getNetworkClass(datacenter)
        print("DATACENTER", datacenter_count, datacenter_scheduling, datacenter_network)

        # return 'start'
        simulationThread = Simulation(
            steps=int(steps),
            town=town,
            radius=float(radius),
            vehicle_count=int(vehicle_count),
            vehicle_fps=int(vehicle_fps),
            vehicle_mapping=vehicle_mapping,
            vehicle_scheduling=vehicle_scheduling,
            vehicle_networking=vehicle_networking,
            rsu_count=int(rsu_count),
            rsu_scheduling=rsu_scheduling,
            rsu_networking=rsu_network,
            datacenter_count=int(datacenter_count),
            datacenter_scheduling=datacenter_scheduling,
            datacenter_networking=datacenter_network
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
                    'mapping': config.VEHICLE_TASK_MAPPING_POLICY.__name__,
                    'scheduling': config.VEHICLE_TASK_SCHEDULING_POLICY.__name__,
                    'networking': config.VEHICLE_NETWORK.__name__
                },
                'rsu': {
                    'count': config.RSU_COUNT,
                    'scheduling': config.RSU_TASK_SCHEDULING_POLICY.__name__,
                    'networking': config.RSU_NETWORK.__name__
                },
                'datacenter': {
                    'count': config.DATACENTER_COUNT,
                    'scheduling': config.DATACENTER_TASK_SCHEDULING_POLICY.__name__,
                    'networking': config.DATACENTER_NETWORK.__name__
                }
            }
    }

    return data
