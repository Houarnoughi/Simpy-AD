"""
Task Mapper
    - keeps refs of every Processing Unit in the simulation context
    - has refs to every task at runtime

    - stores processed Tasks, completed or failed for later stats

We can access their location via
    - Task:
        Task.getCurrentVehicle().getCurrentLocation()
    - Vehicle PU:
        (AGX, TX2).getCurrentVehicle().getCurrentLocation()
    - RSU PU:
        (TeslaV100).getCurrentServer().getParent().getCurrentLocation()
    - DataCenter PU:
        (DGXa100).getCurrentServer().getParent().getCurrentLocation()

    RSU -> Cloud is fastest

    t1, t2, t3
    pu1, pu2, pu3, pu4, pu5

    t3,
"""
from torch import nn
import torch
import numpy as np
import math
from entity.location import Location, Latitude, Longitude
import simpy
from utils.colors import GREEN, END
import random
from Store import Store
from models import TaskMapperNet
from typing import List, TYPE_CHECKING
from entity.cnnModel import CNNModel
from Networking import LTE, LTE_PLUS
import config
import copy
from Exceptions import OutOfMemoryException, NoMoreTasksException
from TaskMappingPolicy import TaskMappingPolicy

torch.set_printoptions(precision=20)

if TYPE_CHECKING:
    from entity.processing_unit import ProcessingUnit
    from entity.task import Task

class TaskMapper:

    pu_list = []
    task_list = []
    all_tasks = []

    nn = TaskMapperNet(input_dim=9, hidden_dim=12, output_dim=1)

    def __init__(self, env: simpy.Environment, taskMappingPolicy: TaskMappingPolicy):
        TaskMapper.env = env
        self.env = env
        self.taskMappingPolicy = taskMappingPolicy
        #self.process = env.process(self.run(env))

    def run(self, env):
        #CYCLE = 0.001
        while True:
            try:
                #Store.log(f"tasks to execute count {Store.getTasksToExecuteCount()}")
                # FIFO
                task: Task = Store.getTask()
                TaskMapper.log(f'Got task {task} from Store')

                sorted_pu_list = Store.getClosestPUforTask(task, config.N_CLOSEST_PU)
                sorted_pu_list = [pu_dist[0] for pu_dist in sorted_pu_list]
                
                # add Vehicle (PU, dist) to the list
                if not config.OFFLOAD_TO_VEHICLE:
                    sorted_pu_list.append(task.getCurrentVehicle().getPU())

                self.taskMappingPolicy.assignToPu(task, sorted_pu_list)
                """
                if config.OFFLOAD:
                    sorted_pu_list = Store.getClosestPUforTask(task, config.N_CLOSEST_PU)
                    sorted_pu_list = [pu_dist[0] for pu_dist in sorted_pu_list]
                    
                    # add Vehicle (PU, dist) to the list
                    if not config.OFFLOAD_TO_VEHICLE:
                        sorted_pu_list.append(task.getCurrentVehicle().getPU())

                    self.taskMappingPolicy.assignToPu(task, sorted_pu_list)
                """
                """
                best_pu: 'ProcessingUnit' = None
                if config.OFFLOAD:
                    # Task's closest n PUs
                    # filtered by config
                    sorted_pu_list = Store.getClosestPUforTask(task, config.N_CLOSEST_PU)

                    # add Vehicle (PU, dist) to the list
                    if not config.OFFLOAD_TO_VEHICLE:
                        sorted_pu_list.append((task.getCurrentVehicle().getPU(), 0))

                    if config.RANDOM:
                        # send to random pu whithin range
                        best_pu, _ = random.choice(sorted_pu_list)
                    else:
                        # (task, pu) props batch
                        tensors = [TaskMapper.taskToTensor(task, pu) for pu, _ in sorted_pu_list]
                        probas = TaskMapper.nn(torch.tensor(tensors).float())
                        probas = probas.detach().numpy()
                        # get index of highest proba PU
                        index = np.argmax(probas)
                        #TaskMapper.log(f"Probas {probas.tolist()}, best index {index}")
                        # sorted_pu_list contains tupples (pu, dist), ignore dist
                        best_pu, _ = sorted_pu_list[index]
                else:
                    # When OFFLOAD is false, we just send back to vehicle's PU
                    best_pu = task.getCurrentVehicle().getPU()
                    
                try:
                    best_pu.submitTask(task)
                    # dump task.pu props before assinging for later stats
                    task_pu_props = TaskMapper.taskPuToDict(task, best_pu)
                    Store.task_pu_props.append( (task, best_pu, task_pu_props) )
                except OutOfMemoryException as e:
                    TaskMapper.log("OutOfMemoryException")
                """
            except IndexError as e:
                TaskMapper.log("No PUs to assign")
                pass
            except NoMoreTasksException as e:
                #TaskMapper.log("NoMoreTasksException")
                #exit()
                pass
                
            yield self.env.timeout(config.TASK_MAPPER_CYCLE)

    def taskPuToDict(task: 'Task', pu: 'ProcessingUnit'):
        inputs_dict = dict()
        inputs_dict['task_id'] = task.id
        inputs_dict["criticality"] = task.criticality.value
        local_pu: ProcessingUnit = task.getCurrentVehicle().getPU()
        local_pu_execution_time = local_pu.getTaskExecutionTime(task)
        inputs_dict["local_pu_execution_time"] = local_pu_execution_time
        remote_pu_execution_time = pu.getTaskExecutionTime(task)
        inputs_dict["remote_pu_execution_time"] = remote_pu_execution_time
        offload_time = LTE.getTransferDuration(task.getSize())
        inputs_dict["offload_time"] = offload_time
        inputs_dict["deadline"] = task.deadline
        inputs_dict["vehicle_pu_queue"] = local_pu.getQueueSize()
        inputs_dict["remote_pu_queue"] = pu.getQueueSize()
        inputs_dict["task_flop"] = task.getFlop()
        inputs_dict["pu_flops"] = pu.getFlops()
        inputs_dict["task_size"] = task.getSize()
        task_location: Location = task.getCurrentVehicle().getCurrentLocation()
        inputs_dict["task_location_lat"] = task_location.getLatitude()
        inputs_dict["task_location_long"] = task_location.getLongitude()
        pu_location: Location = pu.getParent().getLocation()
        inputs_dict["pu_location_lat"] = pu_location.getLatitude()
        inputs_dict["pu_location_long"] = pu_location.getLongitude()
        return inputs_dict

    def taskToTensor(task: 'Task', pu: 'ProcessingUnit') -> List[float]:
        def normalize(data, min, max):
            return (data - min)/(max - min)

        # criticality
        crit = normalize(task.criticality.value, min=1, max=3)
        # execution time
        # local pu execution time
        local_pu: ProcessingUnit = task.getCurrentVehicle().getPU()
        local_pu_execution_time = local_pu.getTaskExecutionTime(task)
        # remote pu execution time
        remote_pu_execution_time = pu.getTaskExecutionTime(task)
        # offloading
        # offload time (bw, distance etc)
        offload_time = LTE.getTransferDuration(task.getSize())

        # pu_queue represents PUs availabilitys based on tasks to process
        # and it's max queue size, range is 0, 1, 2, 3, 0 being the less available
        # Vehicle's PU task queue size (Max=100)
        # vehicle_pu_queue = normalize(local_pu.getAvailability(), 0, 3)
        # Remote PU tasks queue size (Max=100)
        # remote_pu_queue = normalize(pu.getAvailability(), 0, 3)

        # queue
        # for now we take queue_size/max_queue_size
        vehicle_pu_queue = local_pu.getAvailability()
        remote_pu_queue = pu.getAvailability()
        # model props
        # task.flop/pu.flops
        min, max = CNNModel.getModelFlopsMinMax()
        task_flop = normalize(task.getFlop(), min, max)
        # task.size/pu.memory
        min, max = CNNModel.getModelMemoryMinMax()
        task_size = normalize(task.getSize(), min, max)
        # distance
        # task location
        task_location: Location = task.getCurrentVehicle().getCurrentLocation()
        task_lat, task_long = task_location.getLatitudeLongitude()
        # normalization
        task_lat = normalize(task_lat, Latitude.min, Latitude.max)
        task_long = normalize(task_long, Longitude.min, Longitude.max)
        # pu location
        pu_location: Location = pu.getParent().getLocation()
        pu_lat, pu_long = pu_location.getLatitudeLongitude()
        # normalization
        pu_lat = normalize(pu_lat, Latitude.min, Latitude.max)
        pu_long = normalize(pu_long, Longitude.min, Longitude.max)
        # task-pu distance (euclidien)
        distance = math.dist((task_lat, task_long), (pu_lat, pu_long))

        props = [crit, local_pu_execution_time, remote_pu_execution_time,
                 offload_time, vehicle_pu_queue, remote_pu_queue,
                 task_flop, task_size, distance]
        return props

    def log(message):
        print(f"{TaskMapper.env.now}: {GREEN}[TaskMapper] {message}{END}")

    def showTasks():
        TaskMapper.log(f"Tasks {TaskMapper.task_list}")

    def showPUs():
        TaskMapper.log(f"PUs {TaskMapper.pu_list}")

    # returns a list of sorted n closest PUs to a Task (Vehicle) 
    def getClosestPUforTask(task, n) -> List['ProcessingUnit']:
        task_location: Location = task.getCurrentVehicle().getLocation()
        # pu_distance_list = [(pu, Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())) for pu in TaskMapper.pu_list]
        pu_distance_list = []

        pu: ProcessingUnit = None
        for pu in TaskMapper.pu_list:
            dist = Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())
            item = (pu, dist)
            pu_distance_list.append(item)

        return sorted(pu_distance_list, key=lambda item: item[1])[:n]
        
    def assignTaskToPu(self):
        pass
