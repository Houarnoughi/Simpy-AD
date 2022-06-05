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
    
    def getEvenDistributedPoints(src: 'Location', count: int, radius: int) -> list:
        """ get count evenly distributed points around this location """
        RSU_DISTANCE = 200
        CIRCLES = int(radius / RSU_DISTANCE)

        points = []

        for i in range(count):
            #DISTANCE_FROM_CENTER = random.choice(list(range(0, int(radius), 200)))
            #DISTANCE_FROM_CENTER = radius * random.random()
            DISTANCE_FROM_CENTER = radius
            ANGLE = i * 360 / count
            lat, long = hs.inverse_haversine(src.getLatitudeLongitude(), DISTANCE_FROM_CENTER, ANGLE, unit=hs.Unit.METERS)
            points.append(Location("random", lat, long))
        
        return points
    
    def getLocationInRange(src: 'Location', range: float) -> 'Location':
        """ range in meters, get a Location around src within range """
        src_location = (src.getLatitude(), src.getLongitude())

        lat, long = hs.inverse_haversine(src_location, range, 60 * random.random(), hs.Unit.METERS)
        return Location("random", lat, long)

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
    Location("Shangai", 31.230416666666666, 121.47222222222222),
    Location("Los Angeles", 34.05222222222222, -118.24277777777777),
    #Location("Lyon", 45.764043, 4.835658),
    #Location("London", 51.509865, -0.118092),
    #Location("Ney York", 40.7127837, -74.0059413),
    #Location("Tokyo", 35.6894875, 139.6917064),
    #Location("Moscow", 55.755826, 37.617298),
    #Location("Rome", 41.9027835, 12.4963655),
    #Location("Kigali", -1.9484010053997387, 30.0953033638107),
    #Location("Marrakech", 31.62949, -7.984659),
    #Location("Alger", 36.7578, 3.05775),
]