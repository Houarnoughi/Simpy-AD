from flask import Blueprint
from simulation.entity.task import UI_OPTIONS

bp = Blueprint('task', __name__, url_prefix='')

@bp.get('/options')
def taskOptions():

    #response = list(map(lambda o: o.__name__, UI_OPTIONS))
    response = [
        {
            'name': o.__name__,
            'flop': o.FLOP,
            'size': o.SIZE,
            'criticality': o.CRITICALITY.name
        }
        for o in UI_OPTIONS if ( hasattr(o, 'FLOP') and hasattr(o, 'SIZE') and hasattr(o, 'CRITICALITY') )
    ]
    #print("response", response)
    return {
        'task_options': response
    }


@bp.get('/informations')
def taskInfos():

    from entity.task import UI_OPTIONS

    response = [
        {
            'name': o.__name__,
            'flop': o.FLOP,
            'size': o.SIZE,
            'criticality': o.CRITICALITY.name
        }
        for o in UI_OPTIONS if hasattr(o, 'FLOP')
    ]
    #print("response", response)
    return {
        'task_informations': response
    }
