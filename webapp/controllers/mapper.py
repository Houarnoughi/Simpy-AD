from flask import Blueprint
from simulation.task_mapping.task_mapping_policy import UI_OPTIONS

bp = Blueprint('mapper', __name__, url_prefix='')

@bp.get('/options')
def mappingOptions():
    
    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'task_mapping_options': response
    } 