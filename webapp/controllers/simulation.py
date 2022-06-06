from traceback import print_tb
from flask import Blueprint, Flask, request, Request
from Store import Store
from Simulation import Simulation
import config
from Location import Location
from Networking import Network
from TaskSchedulingPolicy import TaskSchedulingPolicy
from TaskMappingPolicy import TaskMappingPolicy
from ProcessingUnit import ProcessingUnit
from Task import Task

bp = Blueprint('simulation', __name__, url_prefix='')

global simulationThread
simulationThread = None


def getTaskMapperClass(request: dict) -> TaskMappingPolicy:
    name = request.get("mapping")

    from TaskMappingPolicy import UI_OPTIONS
    for option in UI_OPTIONS:
        if option.__name__ == name:
            return option


def getTaskSchedulerClass(request: dict) -> TaskSchedulingPolicy:
    name = request.get("scheduling")

    from TaskSchedulingPolicy import UI_OPTIONS
    for option in UI_OPTIONS:
        if option.__name__ == name:
            return option


def getNetworkClass(request: dict) -> Network:
    name = request.get("networking")

    from Networking import UI_OPTIONS
    for option in UI_OPTIONS:
        if option.__name__ == name:
            return option


def getProcessingUnit(request: dict) -> ProcessingUnit:
    name = request.get("processingUnit")

    from ProcessingUnit import UI_OPTIONS
    for option in UI_OPTIONS:
        if option.__name__ == name:
            return option

def getTasks(request: dict) -> list[Task]:
    from Task import UI_OPTIONS

    selected_task_list = request.get("tasks")

    tasks = [option for option in UI_OPTIONS if option.__name__ in selected_task_list]

    return tasks

def getTownLocation(request: Request) -> Location:
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
        vehicle_tasks = getTasks(vehicle)
        vehicle_processing_unit = getProcessingUnit(vehicle)
        vehicle_mapping = getTaskMapperClass(vehicle)
        vehicle_scheduling = getTaskSchedulerClass(vehicle)
        vehicle_networking = getNetworkClass(vehicle)
        print("VEHICLE", vehicle_count, vehicle_fps, vehicle_tasks, vehicle_mapping, vehicle_scheduling, vehicle_networking)

        # RSU
        rsu: dict = request.json.get("rsu")
        rsu_count = rsu.get("count")
        rsu_even_distribution = rsu.get("evenDistribution")
        rsu_processing_unit = getProcessingUnit(rsu)
        rsu_scheduling = getTaskSchedulerClass(rsu)
        rsu_network = getNetworkClass(rsu)
        print("RSU", rsu_count, rsu_even_distribution, rsu_scheduling, rsu_network)

        #return "ok"
        # DATACENTER
        datacenter: dict = request.json.get("datacenter")
        datacenter_count = datacenter.get("count")
        datacenter_processing_unit = getProcessingUnit(datacenter)
        datacenter_scheduling = getTaskSchedulerClass(datacenter)
        datacenter_network = getNetworkClass(datacenter)
        print("DATACENTER", datacenter_count, datacenter_scheduling, datacenter_network)

        #return 'start'
        simulationThread = Simulation(
            steps=int(steps),
            town=town,
            radius=int(radius),
            vehicle_count=int(vehicle_count),
            vehicle_fps=int(vehicle_fps),
            vehicle_tasks=vehicle_tasks,
            vehicle_processing_unit=vehicle_processing_unit,
            vehicle_mapping=vehicle_mapping,
            vehicle_scheduling=vehicle_scheduling,
            vehicle_networking=vehicle_networking,
            rsu_count=int(rsu_count),
            rsu_even_distribution=rsu_even_distribution,
            rsu_processing_unit=rsu_processing_unit,
            rsu_scheduling=rsu_scheduling,
            rsu_networking=rsu_network,
            datacenter_count=int(datacenter_count),
            datacenter_processing_unit=datacenter_processing_unit,
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
                    'tasks': list(map(lambda e: e.__name__, config.VEHICLE_TASKS)),
                    'processingUnit': config.VEHICLE_PROCESSING_UNIT.__name__,
                    'mapping': config.VEHICLE_TASK_MAPPING_POLICY.__name__,
                    'scheduling': config.VEHICLE_TASK_SCHEDULING_POLICY.__name__,
                    'networking': config.VEHICLE_NETWORK.__name__
                },
                'rsu': {
                    'count': config.RSU_COUNT,
                    'evenDistribution': config.RSU_EVEN_DISTRIBUTION,
                    'processingUnit': config.RSU_PROCESSING_UNIT.__name__,
                    'scheduling': config.RSU_TASK_SCHEDULING_POLICY.__name__,
                    'networking': config.RSU_NETWORK.__name__
                },
                'datacenter': {
                    'count': config.DATACENTER_COUNT,
                    'processingUnit': config.DATACENTER_PROCESSING_UNIT.__name__,
                    'scheduling': config.DATACENTER_TASK_SCHEDULING_POLICY.__name__,
                    'networking': config.DATACENTER_NETWORK.__name__
                }
            }
    }

    return data
