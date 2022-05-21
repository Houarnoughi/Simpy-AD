from flask import Blueprint, Flask
from Store import Store
import config

bp = Blueprint('vehicle', __name__, url_prefix='')

@bp.route("/", methods=['GET'])
def getVehicles():

    vehicles = [
        {
            "name": v.name,
            "lat": v.getLocation().latitude,
            "long": v.getLocation().longitude,
            "coordinates": v.getTripCoordinates()
        } for v in Store.vehicle_list
    ]

    return {
        'vehicles': vehicles
    }
    