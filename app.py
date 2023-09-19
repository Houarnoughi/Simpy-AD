from flask import Flask, render_template
from simulation.config import FLASK_SERVER_PORT

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from simulation.webapp.controllers import network, processing_unit, stats, simulation, scheduler, mapper, vehicle, rsu, datacenter, location, task

app = Flask(__name__, template_folder="simulation/webapp/templates")
app.debug = True

app.register_blueprint(stats.bp, url_prefix='/stats')
app.register_blueprint(simulation.bp, url_prefix='/simulation')
app.register_blueprint(scheduler.bp, url_prefix='/scheduler')
app.register_blueprint(mapper.bp, url_prefix='/mapper')
app.register_blueprint(vehicle.bp, url_prefix='/vehicle')
app.register_blueprint(rsu.bp, url_prefix='/rsu')
app.register_blueprint(datacenter.bp, url_prefix='/datacenter')
app.register_blueprint(network.bp, url_prefix='/network')
app.register_blueprint(location.bp, url_prefix='/location')
app.register_blueprint(processing_unit.bp, url_prefix='/processingUnit')
app.register_blueprint(task.bp, url_prefix='/task')

@app.route('/', methods=['GET'])
def index():
    """
    stop running simu if refresh
    """
    simulation.stopSimulation()
    return render_template('ui.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_SERVER_PORT, debug=True)
