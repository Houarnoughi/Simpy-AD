from flask import Blueprint
from simulation.entity.processing_unit import UI_OPTIONS

bp = Blueprint('processingUnit', __name__, url_prefix='')

@bp.get('/options')
def processingUnitOptions():
    
    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'processing_unit_options': response
    }