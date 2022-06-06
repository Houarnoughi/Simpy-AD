"""
This class aims to facilitate model data retrieval
infos about car speed and FPS : Re-thinking CNN Frameworks for Time-SensitiveAutonomous-Driving Applications:
Addressing anIndustrial Challenge
"""
import pandas as pd
from typing import Tuple

class CNNModel(object):
    model_path = ''

    col_name = ['CNN', 'Input_shape', 'Power', 'Memory', 'Latency', 'Input_width', 'Input_size'
        , 'nb_conv_params', 'nb_bn_params', 'nb_fc_params', 'FLOPs', 'nb_layers', 'nb_conv_layers'
        , 'nb_bn_layers', 'nb_fc_layers', 'sum_activations', 'weighted_sum_neurons']

    def __init__(self, name, input_width, model_path='data/models_stats_AGX.csv'):
        self.name = name
        self.input_width = input_width
        self.model_path = model_path
        pass

    # Get the name of the CNN
    def getModelName(self):
        return self.name

    # Get the image input width
    def getInputWidth(self):
        return self.input_width

    # This method returns model characteristics as a dict given its name and input size
    def getModelCharacteristicsDict(self):
        raw_dataset = pd.read_csv(self.model_path, names=self.col_name,
                                  na_values="?", comment='#', sep=",", skipinitialspace=True)
        row = raw_dataset.loc[(raw_dataset['CNN'] == self.getModelName())
                              & (raw_dataset['Input_width'] == self.getInputWidth())]
        return row.iloc[0]

    # Get model flops given its name and input size
    def getModelFLOPS(self):
        return self.getModelCharacteristicsDict()["FLOPs"]

    # Get model memory given its name and input size
    def getModelMemory(self):
        return self.getModelCharacteristicsDict()["Memory"]
    
    """
    Static methods
    """
    @staticmethod
    def getModelFlopsMinMax() -> Tuple[float, float]:
        path = 'data/models_stats_AGX.csv'
        dataset = pd.read_csv(path)
        flops = dataset["FLOPs"]
        return flops.min(), flops.max()

    @staticmethod
    def getModelMemoryMinMax() -> Tuple[float, float]:
        path = 'data/models_stats_AGX.csv'
        dataset = pd.read_csv(path)
        memory = dataset["Memory"]
        return memory.min(), memory.max()

class _CNNModel:
    NAME = None
    FLOP = None
    SIZE = None

    def __init__(self) -> None:
        self.name = self.NAME
        self.flop = self.FLOP
        self.size = self.SIZE

    def getFlop(self) -> int:
        return self.flop
    
    def getSize(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f'[{self.name} flop={self.flop}, size={self.size}]'

class AlexNet(_CNNModel):
    NAME = 'AlexNet'
    FLOP = 1000
    SIZE = 100

class ResNet50(_CNNModel):
    NAME = 'ResNet50'
    FLOP = 2000
    SIZE = 300

if __name__ == '__main__':
    
    m = AlexNet()
    print(m)

    m = ResNet50()
    print(m)

    print(m.getFlop())