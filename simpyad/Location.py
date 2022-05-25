import haversine as hs
from typing import Tuple
import random

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
    
    def getLocationInRange(src: 'Location', range: float) -> 'Location':
        """ range in meters, from UI """
        src_location = (src.getLatitude(), src.getLongitude())

        lat, long = hs.inverse_haversine(src_location, range, random.random(), hs.Unit.METERS)
        return Location("", lat, long)

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

    def json(self) -> dict:
        return {
            'name': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    def __str__(self):
        return f"[Location: {self.latitude}, {self.longitude}]"

    def __repr__(self) -> str:
        return f"[Location: {self.latitude}, {self.longitude}]"


UI_OPTIONS = [
    Location("Lille", 50.631583072533594, 3.057713469569928),
    Location("Paris", 48.857234818870474, 2.3405088720080602),
    Location("Bordeaux", 44.83911345093876, -0.5775176280843897),
    #Location("Lyon", 45.764043, 4.835658),
    #Location("London", 51.509865, -0.118092),
]
