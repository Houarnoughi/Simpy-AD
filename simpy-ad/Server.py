from simpy import Environment
from TaskMapper import TaskMapper

class Server(object):
    idx = 0
    name = ''
    # each server must have its' own PUs, moving to instance var
    #PU_list = []   

    def __init__(self, pu_list, bw, env: Environment, capacity=1):
        self.id = Server.idx
        self.name = f'Server-{Server.idx}'
        Server.idx += 1
        self.pu_list = []
        self.setPUList(pu_list)
        self.bw = bw
        self.env = env
        self.capacity = capacity
        # for pu in self.getPUList():
        #     self.proc = env.process(pu.updateTaskListExecution(15224))

    def getBandwidth(self):
        return self.bw

    def setBandwidth(self, bw):
        self.bw = bw

    def getServerName(self):
        return self.name

    def getPUList(self):
        return self.pu_list

    def setPUList(self, pu_list):
        for pu in pu_list:
            if pu not in self.getPUList():
                pu.setCurrentServer(self)
                self.pu_list.append(pu)

                TaskMapper.addPU(pu)
                print(f'[INFO] Server-setPUList: Processing Unit {pu.getPUName()} added to Server {self.getServerName()}')

    def getTotalFlops(self):
        total = 0
        for pu in self.getPUList():
            total += pu.getFlops()
        return total

    def getTotalMemory(self):
        total = 0
        for pu in self.getPUList():
            total += pu.getMemory()
        return total

    def getTotalPower(self):
        total = 0
        for pu in self.getPUList():
            total += pu.getPower()
        return total

    def __str__(self):
        return f"[ID: {self.id}, {self.name}]"
    
    def __repr__(self) -> str:
        return f"[ID: {self.id}, {self.name}]"