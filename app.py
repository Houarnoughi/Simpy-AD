from pstats import Stats
from flask import Flask, render_template, request
import sys

sys.path.append("./simpyad")

from webapp.controllers import stats, simulation, scheduler, mapper, vehicle, rsu, datacenter, networking, location

app = Flask(__name__, template_folder="webapp/templates")
app.debug = True


app.register_blueprint(stats.bp, url_prefix='/stats')
app.register_blueprint(simulation.bp, url_prefix='/simulation')
app.register_blueprint(scheduler.bp, url_prefix='/scheduler')
app.register_blueprint(mapper.bp, url_prefix='/mapper')
app.register_blueprint(vehicle.bp, url_prefix='/vehicle')
app.register_blueprint(rsu.bp, url_prefix='/rsu')
app.register_blueprint(datacenter.bp, url_prefix='/datacenter')
app.register_blueprint(networking.bp, url_prefix='/networking')
app.register_blueprint(location.bp, url_prefix='/location')

@app.route('/', methods=['GET'])
def index():
    """
    stop running simu if refresh
    """
    simulation.stopSimulation()
    return render_template('ui.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
