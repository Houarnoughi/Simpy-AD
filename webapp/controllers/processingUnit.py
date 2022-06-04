from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config

bp = Blueprint('processingUnit', __name__, url_prefix='')

@bp.get('/options')
def processingUnitOptions():
    
    from ProcessingUnit import UI_OPTIONS
    
    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'processing_unit_options': response
    }