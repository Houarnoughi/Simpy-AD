from flask import Blueprint, request
from simulation.store import Store
from simulation.simulation import Simulation
from simulation import config
from simulation.entity.location import Location

from simulation.utils.network import getNetworkClass
from simulation.task_scheduling.task_scheduling_policy import getSchedulingInstanceByName, getTaskSchedulerClass
from simulation.task_mapping.task_mapping_policy import getMappingInstanceByName, getTaskMapperClass
from simulation.entity.processing_unit import getProcessingUnit

bp = Blueprint('simulation', __name__, url_prefix='')

global simulationThread
simulationThread = None

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
        town = Location.getTownLocation(request)
        print("town", town)

        # Vehicle
        vehicle: dict = request.json.get("vehicle")
        vehicle_count = vehicle.get("count")
        vehicle_fps = vehicle.get("fps")
        vehicle_tasks = vehicle.get("tasks")
        vehicle_processing_unit = getProcessingUnit(vehicle.get("processingUnit"))
        vehicle_mapping = getTaskMapperClass(vehicle.get("mapping"))
        vehicle_scheduling = getTaskSchedulerClass(vehicle.get("scheduling"))
        vehicle_network = getNetworkClass(vehicle.get("network"))
        print("VEHICLE", vehicle_count, vehicle_fps, vehicle_tasks, vehicle_mapping, vehicle_scheduling, vehicle_network)

        # RSU
        rsu: dict = request.json.get("rsu")
        rsu_count = rsu.get("count")
        rsu_even_distribution = rsu.get("evenDistribution")
        rsu_processing_unit = getProcessingUnit(rsu.get("processingUnit"))
        rsu_scheduling = getTaskSchedulerClass(rsu.get("scheduling"))
        rsu_network = getNetworkClass(rsu.get("network"))
        print("RSU", rsu_count, rsu_even_distribution, rsu_scheduling, rsu_network)

        #return "ok"
        # DATACENTER
        datacenter: dict = request.json.get("datacenter")
        datacenter_count = datacenter.get("count")
        datacenter_processing_unit = getProcessingUnit(datacenter.get("processingUnit"))
        datacenter_scheduling = getTaskSchedulerClass(datacenter.get("scheduling"))
        datacenter_network = getNetworkClass(datacenter.get("network"))
        print("DATACENTER", datacenter_count, datacenter_scheduling, datacenter_network)

        # scheduler
        SCHEDULER_QUANTUM = config.SCHEDULER_QUANTUM

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
            vehicle_network=vehicle_network,
            rsu_count=int(rsu_count),
            rsu_even_distribution=rsu_even_distribution,
            rsu_processing_unit=rsu_processing_unit,
            rsu_scheduling=rsu_scheduling,
            rsu_network=rsu_network,
            datacenter_count=int(datacenter_count),
            datacenter_processing_unit=datacenter_processing_unit,
            datacenter_scheduling=datacenter_scheduling,
            datacenter_network=datacenter_network, 
            SCHEDULER_QUANTUM=SCHEDULER_QUANTUM
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

    if simulationThread is None:
        return "not running"

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

    # from ("town", "x", "y") tuple defined in simulation/config.py
    TOWN = Location(*config.TOWN)
    
    data = {
        'simulation':
            {
                'steps': config.SIM_STEPS,
                'town': TOWN.json(),
                'radius': config.RADIUS,
                'vehicle': {
                    'count': config.VEHICLE_COUNT,
                    'fps': config.VEHICLE_FPS,
                    'tasks': config.VEHICLE_TASKS,
                    'processingUnit': config.VEHICLE_PROCESSING_UNIT,
                    'mapping': config.VEHICLE_TASK_MAPPING_POLICY,
                    'scheduling': config.VEHICLE_TASK_SCHEDULING_POLICY,
                    'network': config.VEHICLE_NETWORK
                },
                'rsu': {
                    'count': config.RSU_COUNT,
                    'evenDistribution': config.RSU_EVEN_DISTRIBUTION,
                    'processingUnit': config.RSU_PROCESSING_UNIT,
                    'scheduling': config.RSU_TASK_SCHEDULING_POLICY,
                    'network': config.RSU_NETWORK
                },
                'datacenter': {
                    'count': config.DATACENTER_COUNT,
                    'processingUnit': config.DATACENTER_PROCESSING_UNIT,
                    'scheduling': config.DATACENTER_TASK_SCHEDULING_POLICY,
                    'network': config.DATACENTER_NETWORK
                }
            }
    }

    return data
