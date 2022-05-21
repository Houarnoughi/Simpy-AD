from flask import Blueprint, Flask
from Store import Store
import config

bp = Blueprint('rsu', __name__, url_prefix='')


@bp.route("/", methods=['GET'])
def getRsus():

    rsus = [
        {
            "name": r.name,
            "lat": r.getLocation().latitude,
            "long": r.getLocation().longitude
        } for r in Store.rsu_list
    ]

    return {
        'rsus': rsus
    }
