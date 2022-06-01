import config
from Simulation import Simulation


if __name__ == '__main__':

    steps = config.SIM_STEPS
    town = config.TOWN
    radius = config.RADIUS

    vehicle_count = config.VEHICLE_COUNT
    vehicle_fps = config.VEHICLE_FPS
    vehicle_mapping = config.VEHICLE_TASK_MAPPING_POLICY
    vehicle_scheduling = config.VEHICLE_TASK_SCHEDULING_POLICY
    vehicle_networking = config.VEHICLE_NETWORK

    rsu_count = config.RSU_COUNT
    rsu_even_distribution = config.RSU_EVEN_DISTRIBUTION
    rsu_scheduling = config.RSU_TASK_SCHEDULING_POLICY
    rsu_networking = config.RSU_NETWORK

    datacenter_count = config.DATACENTER_COUNT
    datacenter_scheduling = config.DATACENTER_TASK_SCHEDULING_POLICY
    datacenter_networking = config.DATACENTER_NETWORK
    
    simulation = Simulation(
        # simulation
        steps=1,
        town=town,
        radius=radius,
        # vehicle
        vehicle_count=vehicle_count,
        vehicle_fps=vehicle_fps,
        vehicle_mapping=vehicle_mapping,
        vehicle_scheduling=vehicle_scheduling,
        vehicle_networking=vehicle_networking,
        # rsu
        rsu_count=rsu_count,
        rsu_even_distribution=rsu_even_distribution,
        rsu_scheduling=rsu_scheduling,
        rsu_networking=rsu_networking,
        # datacenter
        datacenter_count=datacenter_count,
        datacenter_scheduling=datacenter_scheduling,
        datacenter_networking=datacenter_networking,
    )
    simulation.run()
    