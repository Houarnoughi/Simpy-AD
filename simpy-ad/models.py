"""
Different models for some use cases

"""
import torch
import torch.nn as nn
import torch.nn.functional as F

class TaskMapperNet(nn.Module):
    """
    Store - receives all tasks 
    TaskMapper gets a task and distributes across PUs
    TaskMapperNet
        input - 
            criticallity (Task)
                1,2,3
            local_pu_execution_time (Task on Vehicle's PU)
                float
            offload_time (Task to PU)
                float
            offload_pu_execution_time (Task on PU)
                float
            offload_execution_time (Task on PU)
                float
            pu_queue (Vehicle PU)
                0 - 500
            pu_queue ??? (PU)
                0 - 1000
            bw (Vehicle to PU)
                
            flop (Task)

            size (Task)

            euclid(task, pu) ???

        output
            offload (threshold)
    """
    def __init__(self, input_dim, hidden_dim, output_dim=1):
        super(TaskMapperNet, self).__init__()

        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, data):
        data = self.fc1(data)
        data = F.relu(data)
        data = self.fc2(data)

        return data