from Location import Location
import simpy
from Colors import RED, END
'''
Notes : Pour la simulation, les principales interactions se font seulement entre les tasks et les PU
'''


class RoadSideUnit(simpy.Resource):
    idx = 0
    name = ''
    server_list = []

    def __init__(self, location: Location, server_list, to_vehicle_bw, to_cloud_bw, env: simpy.Environment, capacity=1):

        self.name = 'RSU-{0}'.format(RoadSideUnit.idx)
        RoadSideUnit.idx += 1
        self.setServerList(server_list)
        self.to_vehicle_bw = to_vehicle_bw
        self.to_cloud_bw = to_cloud_bw
        self.location = location
        self.env = env
        # for server in self.getServerList():
        #     for pu in server.getPUList():
        #         self.proc = env.process(pu.updateTaskListExecution(100))
        super().__init__(env, capacity)
    
    def showInfo(self):
        print(f"{RED}RSU [{self.name}, Servers: {self.server_list} ]{END}")

    # Get the Roadside Unit name
    def getRSUName(self):
        return self.name

    # Get the location of the Roadside Unit
    def getRSULocation(self):
        return self.location

    # Set the location of the Roadside Unit
    def setRSULocation(self, location: Location):
        self.location = location

    # Get the list of the servers of the Roadside Unit
    def getServerList(self):
        return self.server_list

    # Set the list of the servers of the Roadside Unit
    def setServerList(self, server_list):
        for server in server_list:
            if server not in self.getServerList():
                self.server_list.append(server)
                print('[INFO] RoadSideUnit-setServerList: Server {0} added to Roadside Unit {1}'.format(
                    server.getServerName(),
                    self.getRSUName()))