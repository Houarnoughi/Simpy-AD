from Location import Location


class DataCenter(object):
    idx = 0
    name = ''
    server_list = []

    def __init__(self, location: Location, server_list, to_RSU_bw):
        self.name = 'Datacenter-{0}'.format(DataCenter.idx)
        DataCenter.idx += 1
        self.setServerList(server_list)
        self.to_RSU_bw = to_RSU_bw
        self.location = location

    def getDataCenterLocation(self):
        return self.location

    def setDataCenterLocation(self, location: Location):
        self.location = location

    def getDataCenterName(self):
        return self.name

    def getServerList(self):
        return self.server_list

    def setServerList(self, server_list):
        for server in server_list:
            if server not in self.getServerList():
                server.setCurrentDataCenter(self)
                self.server_list.append(server)
                print(
                    '[INFO] DataCenter-setServerList: Server {0} added to Datacenter {1}'.format(server.getServerName(),
                                                                                                 self.getDataCenterName()))

    def getToVehicleBW(self):
        return self.to_RSU_bw

    def setToVehicleBW(self, bw):
        self.to_RSU_bw = bw
