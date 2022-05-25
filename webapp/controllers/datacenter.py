from flask import Blueprint, Flask
from Store import Store
import config

bp = Blueprint('datacenter', __name__, url_prefix='')

@bp.route("/", methods=['GET'])
def getDatacenters():
    
    
    return 'ok'