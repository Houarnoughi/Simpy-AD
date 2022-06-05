from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config

bp = Blueprint('task', __name__, url_prefix='')

@bp.get('/options')
def taskOptions():

    from Task import UI_OPTIONS
    
    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'task_options': response
    }