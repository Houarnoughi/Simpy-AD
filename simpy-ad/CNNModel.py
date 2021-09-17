"""
This class aims to facilitate model data retrieval
infos about car speed and FPS : Re-thinking CNN Frameworks for Time-SensitiveAutonomous-Driving Applications:
Addressing anIndustrial Challenge
"""
import pandas as pd


class CNNModel(object):
    model_path = ''

    col_name = ['CNN', 'Input_shape', 'Power', 'Memory', 'Latency', 'Input_width', 'Input_size'
        , 'nb_conv_params', 'nb_bn_params', 'nb_fc_params', 'FLOPs', 'nb_layers', 'nb_conv_layers'
        , 'nb_bn_layers', 'nb_fc_layers', 'sum_activations', 'weighted_sum_neurons']

    def __init__(self, name, input_width, model_path='../data/models_stats_AGX.csv'):
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
