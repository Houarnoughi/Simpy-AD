from threading import Thread, Condition
from multiprocessing import Process
from time import sleep
import simpy
import random

import sys
sys.path.append('.')

from CNNModel import CNNModel
from Task import _Task, TaskCriticality
from Store import Store
from Location import Location
from Vehicle import Vehicle
from ProcessingUnit import AGX, TeslaV100
from TaskMapper import TaskMapper
import config

class Simulation(Process):
    def __init__(self):
        Process.__init__(self)

    def run(self):
        env = simpy.Environment()

        inception = CNNModel('Inception-v3', 1024)
        resnet18 = CNNModel('ResNet-18', 480)
        mobilenet = CNNModel('MobileNet0.25-v1', 240)

        vehicle_tasks = [
            _Task(flop=inception.getModelFLOPS(), size=inception.getModelMemory(), criticality=TaskCriticality.HIGH),
            #_Task(flop=resnet18.getModelFLOPS(), size=resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            #_Task(flop=mobilenet.getModelFLOPS(), size=mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
            #Task(inception.getModelFLOPS(), inception.getModelMemory(), criticality=TaskCriticality.HIGH),
            #Task(resnet18.getModelFLOPS(), resnet18.getModelMemory(), criticality=TaskCriticality.MEDIUM),
            #Task(mobilenet.getModelFLOPS(), mobilenet.getModelMemory(), criticality=TaskCriticality.LOW),
        ]
        for _ in range(config.VEHICLE_COUNT):
            ## PU init
            pu1 = AGX(task_list=[], scheduler=config.TASK_SCHEDULING_POLICY(config.AGX_QUANTUM), env=env)
            Store.addPU(pu1)

            vehicle = Vehicle(
                c_location=Location("random", random.uniform(config.MIN_LAT, config.MAX_LAT), random.uniform(config.MIN_LONG, config.MAX_LONG)), 
                f_location=Location("Gare Lille", 50.63725143907785, 3.0702985651377745), 
                speed=10, 
                bw = 10e6,
                task_list=vehicle_tasks, 
                PU_list=[pu1], 
                required_FPS=config.FPS, 
                env=env)
            vehicle.showInfo()
            Store.vehicle_list.append(vehicle)

        taskMappingPolicy=config.TASK_MAPPING_POLICY(env=env)
        taskMapper = TaskMapper(env=env, taskMappingPolicy=taskMappingPolicy)

        env.run(until=config.SIM_TIME)

if __name__ == '__main__':
    s = Simulation()
    s.start()

    sleep(4)

    s.terminate()