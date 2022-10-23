from flask import Blueprint
from simulation.utils.network import UI_OPTIONS


bp = Blueprint('network', __name__, url_prefix='')

@bp.get('/options')
def networkOptions():
    
    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'network_options': response
    }