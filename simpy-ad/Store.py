"""
Static class that holds Simulation's that keeps track of
    - all PUs
    - all Tasks
"""
from dataclasses import dataclass
from Colors import END, GREEN, YELLOW, RED, BLUE
from typing import List, TYPE_CHECKING
from Location import Location
import random
import config
import os
from Exceptions import NoMoreTasksException
import Vehicle
import RoadSideUnit
import DataCenter
from requests import post
import math

if TYPE_CHECKING:
    from Task import Task, _Task
    from ProcessingUnit import ProcessingUnit
    from Location import Location

class Store:
    """
    Tasks are assingned to this class on runtime by Vehicles
    Pus are set at the beginning

    TaskMapper gets a task by poping a task from task_list

    later task will be stored in all_tasks for later stats
    """
    vehicle_list = []
    rsu_list = []
    datacenter_list = []

    all_tasks = []
    tasks_to_execute = []
    pu_list = []

    # TaskMapper sends tuple 
    #   task
    #   pu
    #   taskPu props
    task_pu_props = []

    # list of TaskMapperNet inputs dict(task, pu)
    input_list = []

    # lambda expressions to filter tasks
    success_lambda = lambda t: t.isSuccess()
    started_failed_lambda = lambda t: t.isFailed()
    started_not_finished_lambda = lambda t: t.isIncomplete()
    not_started_lambda = lambda t: not t.isStarted()

    def __init__(self, env):
        self.env = env
        #self.proc = env.process(self.run())

    def run(self):
        while True:
            
            vehicles = [
                {
                    "name": v.name,
                    "lat": v.getLocation().latitude,
                    "long": v.getLocation().longitude,
                    "coordinates": v.getTripCoordinates()
                } for v in Store.vehicle_list
            ]
            rsus = [
                {
                    "name": r.name,
                    "lat": r.getLocation().latitude,
                    "long": r.getLocation().longitude
                } for r in Store.rsu_list
            ]
            stats = {
                "all_tasks": Store.getTotalTaskCount(),
                "success_tasks": Store.getSuccessTaskCount(),
                "failed_tasks": Store.getStartedFailedTaskCount(),
                "tasks_to_execute": Store.getTasksToExecuteCount(),
                "incomplete_tasks": Store.getIncompleteTasksCount(),
                "finished_tasks": Store.getSuccessTaskCount(),
                "simulationTime": math.ceil(self.env.now),
                "maxTaskCount": config.MAX_TASK_COUNT
            }
            try:
                post(f"{config.SERVER_URL}/vehicle", json={"vehicles": vehicles})
                post(f"{config.SERVER_URL}/rsu", json={"rsus": rsus})
                post(f"{config.SERVER_URL}/stats", json={"data": stats})
            except Exception as e:
                #print(e)
                pass
            # update every 0.1 sec
            yield self.env.timeout(config.POST_TIMEOUT)

    def log(message):
        print(f'{GREEN}[Store] {message} {END}')

    # FIFO
    def getTask() -> '_Task':
        if Store.tasks_to_execute:
            return Store.tasks_to_execute.pop(0)
        else:
            raise NoMoreTasksException()

    def addTask(task: '_Task'):
        Store.tasks_to_execute.append(task)
        Store.all_tasks.append(task)
        
    def clearTasks():
        Store.tasks_to_execute.clear()

    def addRSU(rsu: 'RoadSideUnit'):
        Store.rsu_list.append(rsu)

    def addPU(pu: 'ProcessingUnit'):
        Store.pu_list.append(pu)
    
    def getTasksToExecuteCount():
        return len(list(filter(Store.not_started_lambda, Store.all_tasks))) if Store.all_tasks else 0
    
    def getIncompleteTasksCount():
        return len(list(filter(Store.started_not_finished_lambda, Store.all_tasks))) if Store.all_tasks else 0

    def getTotalTaskCount():
        return len(Store.all_tasks) if Store.all_tasks else 0

    def getPuCount():
        return len(Store.pu_list)

    def getRandomPU() -> 'ProcessingUnit':
        return random.choice(Store.pu_list)
    
    # returns a list of sorted n closest PUs to a Task (Vehicle) 
    # authorized offload options are defined in config.py
    def getClosestPUforTask(task: '_Task', n) -> List[tuple['ProcessingUnit', float]]:
        task_location: Location = task.getCurrentVehicle().getLocation()
        #pu_distance_list = [(pu, Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())) for pu in TaskMapper.pu_list]
        pu_distance_list = []
        pu_list = []
        
        if config.OFFLOAD_TO_VEHICLE:
            pu_list += list(filter(lambda pu: isinstance(pu.getParent(), Vehicle.Vehicle), Store.pu_list))
        if config.OFFLOAD_TO_RSU:
            pu_list += list(filter(lambda pu: isinstance(pu.getParent(), RoadSideUnit.RoadSideUnit), Store.pu_list))
        if config.OFFLOAD_TO_DATACENTER:
            pu_list += list(filter(lambda pu: isinstance(pu.getParent(), DataCenter.DataCenter), Store.pu_list))
 
        pu: ProcessingUnit = None
        for pu in pu_list:
            dist = Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())
            item = (pu, dist)
            pu_distance_list.append(item)

        return sorted(pu_distance_list, key=lambda item: item[1])[:n]

    def showPUs():
        Store.log(Store.pu_list)
    
    def showTasks():
        pass

    def getStats():
        """
        returns a tuple of numbers of : success, incomplete, fail task
        """
        return None
    
    def getTaskList():
        tasks = Store.all_tasks

    def getSuccessTaskCount():
        return len(list(filter(Store.success_lambda, Store.all_tasks))) if Store.all_tasks else 0

    def getStartedFailedTaskCount():
        return len(list(filter(Store.started_failed_lambda, Store.all_tasks))) if Store.all_tasks else 0

    def getStartedNotFinishedTaskCount():
        return len(list(filter(Store.started_not_finished_lambda, Store.all_tasks))) if Store.all_tasks else 0

    def getNotStartedTaskCount():
        return len(list(filter(Store.not_started_lambda, Store.all_tasks))) if Store.all_tasks else 0

    def export():
        """
        Export statistics to config.OUT_FILE_PATH

        Each csv row contains:
            task properties
            pu properties
            task execution properties (start, end, deadline, duration)
        """
        if not Store.task_pu_props:
            print("Store input list is empty")
            return

        if not os.path.exists(config.OUT_FILE_PATH):
            with open(config.OUT_FILE_PATH, "w") as f:
                pass
        
        for i, (task, pu, data) in enumerate(Store.task_pu_props):
            data["execution_start_time"] = task.execution_start_time
            data["execution_end_time"] = task.execution_end_time
            data["deadline"] = task.deadline
            if task.isSuccess():
                data["state"] = "SUCCESS"
            elif task.isFailed():
                data["state"] = "FAILED"
            elif task.isIncomplete():
                data["state"] = "INCOMPLETE"
            elif not task.isStarted():
                data["state"] = "UNSTARTED"

        # features
        with open(config.OUT_FILE_PATH, "w") as f:
            _, _, sample = Store.task_pu_props[0]
            params = list(sample.keys())
            for param in params:
                f.write(f'{param}')
                f.write(',')
                # if param != params[-1]:
                #     f.write(',')
            f.write('\n')

            for task, pu, input in Store.task_pu_props:
                features = list(input.values())
                #print(features)
                for feature in features:

                    f.write(str(feature))
                    f.write(',')
                    # if feature != features[-1]:
                    #     f.write(',')
                f.write('\n')
    
    def clear():
        Store.vehicle_list.clear()
        Store.rsu_list.clear()
        Store.datacenter_list.clear()
        Store.all_tasks.clear()
        Store.tasks_to_execute.clear()
        Store.pu_list.clear()
        Store.task_pu_props.clear()
        Store.input_list.clear()

    def showStats():
        print("\n")
        print("-------------------- Stats ----------------------")
        # success
        # print(f'{GREEN}Success tasks')

        tasks = Store.all_tasks
        t: _Task = None

        success_list = list(filter(Store.success_lambda, tasks))
        # for t in ended_list:
        #     print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop, {t.currentPU}')

        started_failed_list = list(filter(Store.started_failed_lambda, tasks))
        # for t in started_not_ended_list:
        #     print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop, {t.currentPU}')

        started_not_finished_list = list(filter(Store.started_not_finished_lambda, tasks))

        # print(f'{RED}Not started tasks')
        not_started_list = list(filter(Store.not_started_lambda, tasks))
        # for t in not_started_list:
        #     print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop, {t.currentPU}')
        print(Store.pu_list)
        pu: 'ProcessingUnit'
        for pu in Store.pu_list:
            pu.show_stats()

        print(f'{GREEN}Tasks started and finished before fixed deadline {len(success_list)}') 
        print(f'{YELLOW}Tasks finished after fixed deadline {len(started_failed_list)}')  
        print(f'{BLUE}Tasks started but not finished {len(started_not_finished_list)}') 
        print(f'{RED}Not started tasks {len(not_started_list)}') 

        print(f"{YELLOW}-------------------- Stats ----------------------")

        #return len(ended_list), len(started_not_ended_list), len(not_started_list)