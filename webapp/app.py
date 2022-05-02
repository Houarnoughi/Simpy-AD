from flask import Flask, render_template
import os
import random
import sys
sys.path.insert(1, "../simpy-ad")
import config

app = Flask(__name__)
app.debug = True


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/vehicle/all', methods=['GET'])
def getVehicles():
    data = {
        "vehicles": [
            {"id": 1, "name": "vehicle1", "location": {"lat": random.uniform(
                config.MIN_LAT, config.MAX_LAT), "long": random.uniform(config.MIN_LONG, config.MAX_LONG)}},
            {"id": 2, "name": "vehicle2", "location": {"lat": random.uniform(
                config.MIN_LAT, config.MAX_LAT), "long": random.uniform(config.MIN_LONG, config.MAX_LONG)}},
            {"id": 3, "name": "vehicle3", "location": {"lat": random.uniform(
                config.MIN_LAT, config.MAX_LAT), "long": random.uniform(config.MIN_LONG, config.MAX_LONG)}}
        ]
    }
    return data

@app.route('/rsu/all', methods=['GET'])
def getRsus():
    data = {
        "rsus": [
            {"id": 1, "name": "RSU_1", "location": {"lat": 50.63222755233801, "long": 3.0628195821035655}},
            {"id": 1, "name": "RSU_1", "location": {"lat": 50.64099393427632, "long": 3.044548801247785}}
        ]
    }
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
