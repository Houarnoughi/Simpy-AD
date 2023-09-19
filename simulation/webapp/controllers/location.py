from flask import Blueprint
from simulation.entity.location import UI_OPTIONS

bp = Blueprint('location', __name__, url_prefix='')

@bp.get('/options')
def locationOptions():

    response = list(map(lambda o: o.json(), UI_OPTIONS))
    #print("response", response)
    return {
        'location_options': response
    }