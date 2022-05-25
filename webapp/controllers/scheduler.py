from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config

bp = Blueprint('scheduler', __name__, url_prefix='')

@bp.get('/options')
def schedulerOptions():

    from TaskSchedulingPolicy import UI_OPTIONS
    
    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'task_scheduling_options': response
    }