from flask import Blueprint
from simulation.task_scheduling.task_scheduling_policy import UI_OPTIONS


bp = Blueprint('scheduler', __name__, url_prefix='')

@bp.get('/options')
def schedulerOptions():

    response = list(map(lambda o: o.__name__, UI_OPTIONS))
    #print("response", response)
    return {
        'task_scheduling_options': response
    }