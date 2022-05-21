from pstats import Stats
from flask import Flask, render_template, request
import os
import random
import sys
from Simulation import Simulation
from numpy import vectorize
from controllers import stats, simulation, scheduler, mapper, vehicle, rsu, datacenter

sys.path.insert(1, "../simpy-ad")
import config
from Store import Store

app = Flask(__name__)
app.debug = True

app.register_blueprint(stats.bp, url_prefix='/stats')
app.register_blueprint(simulation.bp, url_prefix='/simulation')
app.register_blueprint(scheduler.bp, url_prefix='/scheduler')
app.register_blueprint(mapper.bp, url_prefix='/mapper')
app.register_blueprint(vehicle.bp, url_prefix='/vehicle')
app.register_blueprint(rsu.bp, url_prefix='/rsu')
app.register_blueprint(datacenter.bp, url_prefix='/datacenter')

print(app.blueprints.keys())

@app.route('/', methods=['GET'])
def index():
    """
    stop running simu if refresh
    """
    simulation.stopSimulation()
    return render_template('ui.html')


# global vars
global vehicles
vehicles = []
global rsus
rsus = []

"""
From Simulation
"""
@app.route('/vehicle', methods=['POST'])
def updateVehicles():
    global vehicles

    newVehicles = request.json.get('vehicles', [])
    vehicles = newVehicles

    return "ok"

@app.route('/rsu', methods=['POST'])
def updateRsus():
    global rsus

    newRsus = request.json.get('rsus', [])
    rsus = newRsus

    return "ok"

"""
UI ajax
"""
@app.route('/vehicle/all', methods=['GET'])
def getVehicles():
    global vehicles
    data = {
        "vehicles": vehicles
    }
    return data

@app.route('/rsu/all', methods=['GET'])
def getRsus():
    global rsus
    data = {
        "rsus": rsus
    }
    return data



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
