"""
Map related implementations

path planner etc
"""
import requests
from Location import Location
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Location import Location

class OpenStreetAPI:
    URI = 'https://api.openrouteservice.org'
    TOKEN = '5b3ce3597851110001cf62480a421079db594016b4d5c12fc6980fcd'
    REQUEST_HEADERS = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    }

class PathPlanner(object):
    """
    Path planner
    """
    def getPath(start_node: 'Location', end_node: 'Location'):
        """
        Returns trip coordinates between 2 Locations
        """
        startLat, startLong = start_node.getLatitudeLongitude()
        endLat, endLong = end_node.getLatitudeLongitude()

        res = requests.get(f'{OpenStreetAPI.URI}/v2/directions/driving-car?api_key={OpenStreetAPI.TOKEN}&start={startLat},{startLong}&end={endLat},{endLong}', headers=OpenStreetAPI.REQUEST_HEADERS)

        print(res.json().get('features')[0].get('geometry').get('coordinates'))
        
        coordinates = []

        return coordinates

if __name__ == "__main__":
    res = PathPlanner.getPath(Location("", 8.681495, 49.41461), Location("", 8.687872, 49.420318))