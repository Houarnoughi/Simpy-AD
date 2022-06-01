"""
Map related implementations

path planner etc
"""
import config
import requests
from Location import Location
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Location import Location

class OpenStreetAPI:
    URI = 'https://api.openrouteservice.org'
    TOKEN = config.ORS_TOKEN
    REQUEST_HEADERS = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
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

        response = requests.get(
            f'{OpenStreetAPI.URI}/v2/directions/driving-car?api_key={OpenStreetAPI.TOKEN}&start={startLong},{startLat}&end={endLong},{endLat}', 
            headers=OpenStreetAPI.REQUEST_HEADERS
        )
        json = response.json()

        coordinates = []

        if json.get('error'):
            print("Path error ", json.get('error').get('message'))
        else:
            coordinates = response.json().get('features')[0].get('geometry').get('coordinates')

        return coordinates

if __name__ == "__main__":
    res = PathPlanner.getPath(Location("", 8.681495, 49.41461), Location("", 8.687872, 49.420318))