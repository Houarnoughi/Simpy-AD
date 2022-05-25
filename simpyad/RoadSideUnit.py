from Location import Location
import simpy
from Colors import RED, END
from typing import List
from Server import Server
'''
Notes : Pour la simulation, les principales interactions se font seulement entre les tasks et les PU
'''

"""
activity_range - a number in meters representing RSU's activity zone as a circle
to_vehicle_bw - 
to_cloud_bw - 
"""
class RoadSideUnit(simpy.Resource):
    idx = 1
    name = ''
    #server_list = []

    def __init__(self, location: Location, server_list: List[Server], to_vehicle_bw, to_cloud_bw, env: simpy.Environment, activity_range=0, capacity=1):
        self.id = RoadSideUnit.idx
        self.name = f'RSU-{self.id}'
        RoadSideUnit.idx += 1
        self.server_list = []
        self.setServerList(server_list)
        self.to_vehicle_bw = to_vehicle_bw
        self.to_cloud_bw = to_cloud_bw
        self.location = location
        self.activity_range = activity_range
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

    def setLocation(self, location: Location):
        self.location=location

    def getLocation(self) -> Location:
        return self.location

    # Get the list of the servers of the Roadside Unit
    def getServerList(self) -> List[Server]:
        return self.server_list

    # Set the list of the servers of the Roadside Unit
    def setServerList(self, server_list: List[Server]):
        server: Server = None
        for server in server_list:
            if server not in self.getServerList():
                self.server_list.append(server)
                print(f'[INFO] RoadSideUnit-setServerList: Server {server.getServerName()} added to Roadside Unit {self.getRSUName()}')
                #server.setParent(self)
                for pu in server.getPUList():
                    pu.setParent(self)

    def __str__(self):
        return f"[ID: {self.id}, {self.name}]"
    
    def __repr__(self) -> str:
        return f"[ID: {self.id}, {self.name}]"