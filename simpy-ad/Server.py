from simpy import Environment


class Server(object):
    idx = 0
    name = ''
    PU_list = []

    def __init__(self, PU_list, bw, env: Environment, capacity=1):
        self.name = 'Server-{0}'.format(Server.idx)
        Server.idx += 1
        self.setPUList(PU_list)
        self.bw = bw
        self.env = env
        self.capacity = capacity
        for pu in self.getPUList():
            self.proc = env.process(pu.updateTaskListExecution(15224))

    def getBandwidth(self):
        return self.bw

    def setBandwidth(self, bw):
        self.bw = bw

    def getServerName(self):
        return self.name

    def getPUList(self):
        return self.PU_list

    def setPUList(self, PU_list):
        for pu in PU_list:
            if pu not in self.getPUList():
                pu.setCurrentServer(self)
                self.PU_list.append(pu)
                print('[INFO] Server-setPUList: Processing Unit {0} added to Server {1}'.format(pu.getPUName(),
                                                                                                self.getServerName()))

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
