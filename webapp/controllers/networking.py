from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config

bp = Blueprint('networking', __name__, url_prefix='')

@bp.get('/options')
def networkingOptions():

    from Networking import UI_OPTIONS
    
    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'networking_options': response
    }