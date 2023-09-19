"""
Map related implementations

path planner etc
"""
from simulation.config import ORS_TOKEN
import requests
from abc import ABC, abstractmethod
from simulation.entity.location import Location
from typing import List, Tuple

class OpenStreetAPI:
    URI = 'https://api.openrouteservice.org'
    TOKEN = ORS_TOKEN
    REQUEST_HEADERS = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8'
    }

class PathPlanner(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def getPath(start_node: Location, end_node: Location) -> List[Tuple[float, float]]:
        """ impl by subclass """

class ORSPathPlanner(PathPlanner):
    """
    OpenStreetAPI response object:

    {
        type: FeatureCollection,
        features: [
            {
                type: Feature,
                bbox: ,
                properties: ,
                geometry: {
                    type: LineString,
                    coordinates: [
                        [8.666, 4.343]
                        ...
                    ]
                }
            }
        ],
        bbox: ,
        metadata: 
    }
    """
    def getPath(self, start_node: Location, end_node: Location) -> List[Tuple[float, float]]:
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
            print("Path error ", json.get('error'))
        else:
            coordinates = response.json().get(
                'features')[0].get('geometry').get('coordinates')

        return coordinates


if __name__ == "__main__":
    res = PathPlanner.getPath(
        Location("", 8.681495, 49.41461), Location("", 8.687872, 49.420318))
