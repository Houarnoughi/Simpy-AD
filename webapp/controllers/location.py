from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config

bp = Blueprint('location', __name__, url_prefix='')

@bp.get('/options')
def locationOptions():

    from Location import UI_OPTIONS
    
    response = list(map(lambda o: o.json(), UI_OPTIONS))
    #print("response", response)
    return {
        'location_options': response
    }