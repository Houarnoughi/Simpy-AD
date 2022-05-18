import haversine as hs
from typing import Tuple

class Latitude:
    min = -90
    max = 90

class Longitude:
    min = -180
    max = 180

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
    
    def getDistanceInMetersBetween(src: 'Location', dst: 'Location'):
        source = (src.getLatitude(), src.getLongitude())
        dst_location = (dst.getLatitude(), dst.getLongitude())
        return hs.haversine(source, dst_location, hs.Unit.METERS)

    def getDistanceInMeters(self, dst: 'Location'):
        src = (self.getLatitude(), self.getLongitude())
        dst_location = (dst.getLatitude(), dst.getLongitude())
        return hs.haversine(src, dst_location, hs.Unit.METERS)

    def getDistanceInKm(self, dst: 'Location'):
        src = (self.getLatitude(), self.getLongitude())
        dst_location = (dst.getLatitude(), dst.getLongitude())
        return hs.haversine(src, dst_location)
    
    def getDistanceInKmFromTuples(src: Tuple[float, float], dst: Tuple[float, float]) -> float:
        return hs.haversine(src, dst)

    def getLatitudeLongitude(self) -> Tuple[float, float]:
        return self.getLatitude(), self.getLongitude()

    def __str__(self):
        return f"[Location: {self.latitude}, {self.longitude}]"
    
    def __repr__(self) -> str:
        return f"[Location: {self.latitude}, {self.longitude}]"
