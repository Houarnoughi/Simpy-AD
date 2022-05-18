from pstats import Stats
from flask import Flask, render_template, request
import os
import random
import sys
from Simulation import Simulation

from numpy import vectorize
sys.path.insert(1, "../simpy-ad")
import config

app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# global vars
global vehicles
vehicles = []
global rsus
rsus = []

global simulation
simulation = None

@app.post('/simulation/start')
def startSimulation():
    try:
        print("starting simulation with ", request.json)
        global simulation

        if simulation:
            print("already running a simu, please stop it first")
            return "already running a simu, please stop it first"
        simulation = Simulation()
        simulation.start()
        return "started"
    except Exception as e:
        print(e)
        return "error"

@app.post('/simulation/stop')
def stopSimulation():
    print("stopping simulation")
    global simulation
    try:
        simulation.terminate()
        simulation = None
        return "stopped"
    except Exception as e:
        print(e)
        return "error"

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

# stats
global stats 
stats = dict()

@app.route('/stats', methods=['POST'])
def setStats():
    global stats

    newStats = request.json.get('data', {})
    stats = newStats

    return "ok"

@app.route('/stats', methods=['GET'])
def getStats():
    global stats
    
    return stats

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
