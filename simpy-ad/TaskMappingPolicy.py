from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import random
import simpy
from Colors import END, GREEN
import torch
import torch.nn as nn
import torch.nn.functional as F
import Networking
from CNNModel import CNNModel
from Location import Location, Latitude, Longitude
import math
import numpy as np
import config

if TYPE_CHECKING:
    from Task import _Task
    from ProcessingUnit import ProcessingUnit


class TaskMappingPolicy(ABC):
    """
    Abstract class for task mapping policy.

    Exceptions to catch:
        - IndexError, if somehow PU_list is empty
        - OutOfMemoryException, if PU is out of memory
        - Exception, if ever

    assignToPu must be implemented by each policy
    """

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.proc = env.process(self.run())

    def run(self):
        while True:
            self.callback()
            yield self.env.timeout(config.TASK_MAPPING_CALLBACK_INTERVAL)
    
    def callback(self):
        """
        Callback method to be implemented by each policy

        You can override this callback in child classes to do whatever you want 
        every config.TASK_MAPPING_CALLBACK_INTERVAL steps defined in config.py

        - optimize your model
        - show stats etc
        """
        pass 
        

    @abstractmethod
    def assignToPu(self, task: '_Task', PU_list: list['ProcessingUnit']):
        """ com """
        raise NotImplemented("Please implement this method")

    def log(self, msg: str):
        print(f'{self.env.now}: {GREEN}{self.__class__.__name__}: {msg}{END}')


class RandomTaskMappingPolicy(TaskMappingPolicy):
    """
    Randomly assign a task to one of PUs
    """

    def assignToPu(self, task: '_Task', pu_list: list['ProcessingUnit']):
        random_pu: 'ProcessingUnit' = random.choice(pu_list)
        random_pu.submitTask(task)
    

class InplaceMappingPolicy(TaskMappingPolicy):
    """
    Get tasks vehicle's main PU and assign task to it
    """

    def assignToPu(self, task: '_Task', pu_list: list['ProcessingUnit'] = None):
        vehicle_pu: 'ProcessingUnit' = task.getCurrentVehicle().getPU()
        vehicle_pu.submitTask(task)

"""
Custom
"""
class TaskMapperNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(TaskMapperNet, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        return x

class CustomTaskMappingPolicy(TaskMappingPolicy):
    def __init__(self, env: simpy.Environment):
        super().__init__(env)
        self.nn = TaskMapperNet(input_dim=9, hidden_dim=12, output_dim=1)

    def callback(self):
        self.log('callback called')
        #input()

    def assignToPu(self, task: '_Task', pu_list: list['ProcessingUnit'] = None):
        inputs = [self.convertToFeatureVector(task, pu) for pu in pu_list]
        probas: torch.Tensor = self.nn(torch.tensor(inputs).float())
        probas = probas.detach().numpy()
        # get index of highest proba PU
        index = np.argmax(probas)
        self.log(f"Probas {probas.tolist()}, best index {index}")
        # sorted_pu_list contains tupples (pu, dist), ignore dist
        best_pu: 'ProcessingUnit' = pu_list[index]
        best_pu.submitTask(task)
    
    def convertToFeatureVector(self, task: '_Task', pu: 'ProcessingUnit'):
        """
        Convert task and pu to 1D feature vector
        """
        def normalize(data, min, max):
            return (data - min)/(max - min)

        criticality = task.getCriticality().value
        local_pu: ProcessingUnit = task.getCurrentVehicle().getPU()
        # local pu execution time
        local_pu_execution_time = local_pu.getTaskExecutionTime(task) 
        # remote pu execution time
        remote_pu_execution_time = pu.getTaskExecutionTime(task)
        # offload time (bw, distance etc)
        offload_time = config.NETWORK.getTransferDuration(task.getSize())
        # for now we take queue_size/max_queue_size
        vehicle_pu_queue = local_pu.getAvailability()
        remote_pu_queue = pu.getAvailability()
        # task.flop/pu.flops
        min, max = CNNModel.getModelFlopsMinMax()
        task_flop = normalize(task.getFlop(), min, max)
        # task.size/pu.memory
        min, max = CNNModel.getModelMemoryMinMax()
        task_size = normalize(task.getSize(), min, max)
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

        features = [criticality, local_pu_execution_time, remote_pu_execution_time,
                 offload_time, vehicle_pu_queue, remote_pu_queue,
                 task_flop, task_size, distance]
        #print(features)
        return features

if __name__ == "__main__":
    env = simpy.Environment()
    r = CustomTaskMappingPolicy(env=env)
    