from pstats import Stats
from flask import Flask, render_template, request
import os
import random
import sys
from Simulation import Simulation

from numpy import vectorize
sys.path.insert(1, "../simpy-ad")
import config
from Store import Store

app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET'])
def index():
    #return render_template('index.html')
    return render_template('ui.html')


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
        global simulation

        if simulation:
            print("already running a simu, please stop it first")
            return "already running a simu, please stop it first"
        
        print(request.json)
        steps = request.json.get("steps", 99)
        vehicle_count = request.json.get("vehicle_count", 99)
        vehicle_fps = request.json.get("vehicle_fps", 99)
        simulation = Simulation(
            steps=int(steps), 
            vehicle_count=int(vehicle_count), 
            vehicle_fps=int(vehicle_fps)
        )
        simulation.start()
        return "started"
    except Exception as e:
        print("app.startSimulation ", e)
        return "error"

@app.post('/simulation/stop')
def stopSimulation():
    print("stopping simulation")
    global simulation
    try:
        simulation.stop()
        simulation = None

        Store.clear()

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

@app.route('/stats', methods=['GET'])
def getStats():
    stats = {
        "all_tasks": Store.getTotalTaskCount(),
        "success_tasks": Store.getSuccessTaskCount(),
        "failed_tasks": Store.getStartedFailedTaskCount(),
        "tasks_to_execute": Store.getTasksToExecuteCount(),
        "incomplete_tasks": Store.getIncompleteTasksCount(),
        "finished_tasks": Store.getSuccessTaskCount(),
        "maxTaskCount": config.MAX_TASK_COUNT
    }
    return stats

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
