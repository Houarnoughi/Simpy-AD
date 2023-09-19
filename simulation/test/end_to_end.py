import unittest
import random
import simpy
from simulation.entity.vehicle import Vehicle
from simulation.entity.location import Location
from simulation.entity import ProcessingUnit, AGX
from simulation.task_mapping import InplaceMappingPolicy
from simulation.task_scheduling import FIFOSchedulingPolicy
from simulation.task_scheduling import SJFSchedulingPolicy
from simulation.task_scheduling import RoundRobinSchedulingPolicy
from simulation.service.map_service import ORSPathPlanner

class VehicleTest(unittest.TestCase):
    def test_fifo(self):
        town = Location("Lille", 50.63227795984094, 3.0565110919603784)
        Location.getLocationInRange(town, 100)

        env = simpy.Environment()

        pu = AGX(
            scheduler=FIFOSchedulingPolicy(),
            env=env
        )

        v = Vehicle(
            c_location=Location.getLocationInRange(
                town, random.randint(0, 30)),
            f_location=Location.getLocationInRange(
                town, random.randint(0, 30)),
            speed=10,
            bw=10e6,
            task_list=[
                "MappingTask", 
                #"TrafficSignDetectionTask"
            ],
            PU_list=[pu],
            task_mapping_policy=InplaceMappingPolicy(env),
            path_planner=ORSPathPlanner(),
            required_FPS=10,
            env=env
        )

        #for i in range(10):
        while env.now < 2:
            #print("env.now=", env.now)
            env.step()

        print(f"{pu.getQueueSize()=}, {len(pu.getTaskList())=}")

if __name__ == '__main__':
    unittest.main()
