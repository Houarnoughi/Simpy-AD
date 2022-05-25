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

            Add pu_max_queue_size in ProcessingUnit. 
            Define tresholds - categorical instead of min max

            For pu_max_queue_size=100, availability is
                if actual_queue_size is 25% -> HIGH 3
                if actual_queue_size is 50% -> MEDIUM 2
                if actual_queue_size is 75% -> LOW 1
                if actual_queue_size is >75% -> None 0

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

        return torch.sigmoid(data)

if __name__ == "__main__":
    pass

