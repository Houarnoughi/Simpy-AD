from flask import Blueprint

bp = Blueprint('datacenter', __name__, url_prefix='')

@bp.route("/", methods=['GET'])
def getDatacenters():
    
    
    return 'ok'