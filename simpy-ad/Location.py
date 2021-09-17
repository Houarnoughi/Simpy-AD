import haversine as hs

class Location(object):

    def __init__(self, address, latitude, longitude):
        self.address = address
        self.latitude = latitude
        self.longitude = longitude

    def getAddress(self):
        return self.address

    def setAddress(self, address):
        self.address = address

    def getLatitude(self):
        return self.latitude

    def setLatitude(self, latitude):
        self.latitude = latitude

    def getLongitude(self):
        return self.longitude

    def setLongitude(self, longitude):
        self.longitude = longitude

    def getDistanceInKm(self, dst):
        src = (self.getLatitude(), self.getLongitude())
        coord = (dst.getLatitude(), dst.getLongitude())
        return hs.haversine(src, coord)
