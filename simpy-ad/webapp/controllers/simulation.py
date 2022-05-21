from flask import Blueprint, Flask, request
from Store import Store
from Simulation import Simulation
import config

bp = Blueprint('simulation', __name__, url_prefix='')

global simulationThread
simulationThread = None

@bp.post('/start')
def startSimulation():
    try:
        global simulationThread

        if simulationThread:
            print("already running a simu, please stop it first")
            return "already running a simu, please stop it first"
        
        print(request.json)
        steps = request.json.get("steps", 99)
        vehicle_count = request.json.get("vehicle_count", 99)
        vehicle_fps = request.json.get("vehicle_fps", 99)
        simulationThread = Simulation(
            steps=int(steps), 
            vehicle_count=int(vehicle_count), 
            vehicle_fps=int(vehicle_fps)
        )
        simulationThread.start()
        return "started"
    except Exception as e:
        print("app.startSimulation ", e)
        return "error"

@bp.post('/stop')
def stopSimulation():
    print("stopping simulation")
    global simulationThread
    try:
        simulationThread.stop()
        simulationThread = None

        Store.clear()

        return "stopped"
    except Exception as e:
        print(e)
        return "error"