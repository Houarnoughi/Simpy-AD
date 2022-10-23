
from simulation import config
from simulation.simulation import Simulation
from simulation.entity.location import Location
from simulation.task_scheduling.task_scheduling_policy import getTaskSchedulerClass
from simulation.task_mapping.task_mapping_policy import getTaskMapperClass
from simulation.entity.processing_unit import getProcessingUnit
from simulation.utils.network import getNetworkClass

if __name__ == '__main__':

    steps = config.SIM_STEPS
    
    # from ("town", "x", "y") tuple defined in simulation/config.py
    town = Location(*config.TOWN)

    radius = config.RADIUS

    vehicle_count = config.VEHICLE_COUNT
    vehicle_fps = config.VEHICLE_FPS
    vehicle_tasks = config.VEHICLE_TASKS
    vehicle_processing_unit = getProcessingUnit(config.VEHICLE_PROCESSING_UNIT)
    vehicle_mapping = getTaskMapperClass(config.VEHICLE_TASK_MAPPING_POLICY)
    vehicle_scheduling = getTaskSchedulerClass(config.VEHICLE_TASK_SCHEDULING_POLICY)
    vehicle_network = getNetworkClass(config.VEHICLE_NETWORK)

    rsu_count = config.RSU_COUNT
    rsu_even_distribution = config.RSU_EVEN_DISTRIBUTION
    rsu_processing_unit = getProcessingUnit(config.RSU_PROCESSING_UNIT)
    rsu_scheduling = getTaskSchedulerClass(config.RSU_TASK_SCHEDULING_POLICY)
    rsu_network = getNetworkClass(config.RSU_NETWORK)

    datacenter_count = config.DATACENTER_COUNT
    datacenter_processing_unit = getProcessingUnit(config.DATACENTER_PROCESSING_UNIT)
    datacenter_scheduling = getTaskSchedulerClass(config.DATACENTER_TASK_SCHEDULING_POLICY)
    datacenter_network = getNetworkClass(config.DATACENTER_NETWORK)

    SCHEDULER_QUANTUM = config.SCHEDULER_QUANTUM
    
    simulation = Simulation(
        # simulation
        steps=steps,
        town=town,
        radius=radius,
        # vehicle
        vehicle_count=vehicle_count,
        vehicle_fps=vehicle_fps,
        vehicle_tasks=vehicle_tasks,
        vehicle_processing_unit=vehicle_processing_unit,
        vehicle_mapping=vehicle_mapping,
        vehicle_scheduling=vehicle_scheduling,
        vehicle_network=vehicle_network,
        # rsu
        rsu_count=rsu_count,
        rsu_even_distribution=rsu_even_distribution,
        rsu_processing_unit=rsu_processing_unit,
        rsu_scheduling=rsu_scheduling,
        rsu_network=rsu_network,
        # datacenter
        datacenter_count=datacenter_count,
        datacenter_processing_unit=datacenter_processing_unit,
        datacenter_scheduling=datacenter_scheduling,
        datacenter_network=datacenter_network,
        # sched
        SCHEDULER_QUANTUM=SCHEDULER_QUANTUM
    )
    simulation.run()
    