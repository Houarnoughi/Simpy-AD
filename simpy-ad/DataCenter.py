from Location import Location
from typing import List
from Server import Server

class DataCenter(object):
    idx = 0
    name = ''
    server_list = []

    def __init__(self, location: Location, server_list: List[Server], to_RSU_bw):
        self.id = DataCenter.idx
        self.name = f'Datacenter-{self.id}'
        DataCenter.idx += 1
        self.setServerList(server_list)
        self.to_RSU_bw = to_RSU_bw
        self.location = location

    def getDataCenterLocation(self) -> Location:
        return self.location

    def setDataCenterLocation(self, location: Location):
        self.location = location

    def getDataCenterName(self):
        return self.name

    def getServerList(self) -> List[Server]:
        return self.server_list

    def setServerList(self, server_list: List[Server]):
        server: Server = None
        for server in server_list:
            if server not in self.getServerList():
                server.setCurrentDataCenter(self)
                self.server_list.append(server)
                print(f'[INFO] DataCenter-setServerList: Server {server.getServerName()} added to Datacenter {self.getDataCenterName()}')

    def getToVehicleBW(self):
        return self.to_RSU_bw

    def setToVehicleBW(self, bw):
        self.to_RSU_bw = bw

    def setLocation(self, location: Location):
        self.location=location

    def getLocation(self) -> Location:
        return self.location

    def __str__(self):
        return f"[ID: {self.id}, {self.name}]"
    
    def __repr__(self) -> str:
        return f"[ID: {self.id}, {self.name}]"
