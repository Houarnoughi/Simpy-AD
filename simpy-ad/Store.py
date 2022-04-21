"""
Static class that holds Simulation's that keeps track of
    - all PUs
    -  all Tasks
"""
from Colors import END, GREEN, YELLOW, RED
from typing import List, TYPE_CHECKING
from Location import Location
import random
import matplotlib.pyplot as plt
import TaskMapper

if TYPE_CHECKING:
    from Task import Task
    from ProcessingUnit import ProcessingUnit
    from Location import Location

class Store:
    """
    Tasks are assingned to this class on runtime by Vehicles
    Pus are set at the beginning

    TaskMapper gets a task by poping a task from task_list

    later task will be stored in all_tasks for later stats
    """
    all_tasks = []
    task_list = []
    pu_list = []

    def log(message):
        print(f'{GREEN}[Store] {message} {END}')

    # FIFO
    def getTask() -> 'Task':
        return Store.task_list.pop(0)

    def addTask(task: 'Task'):
        Store.all_tasks.append(task)
        Store.task_list.append(task)

    def addPU(pu: 'ProcessingUnit'):
        Store.pu_list.append(pu)
    
    def getTaskCount():
        return len(Store.task_list)

    def getPuCount():
        return len(Store.pu_list)

    def getRandomPU() -> 'ProcessingUnit':
        return random.choice(Store.pu_list)
    
    # returns a list of sorted n closest PUs to a Task (Vehicle) 
    def getClosestPUforTask(task: 'Task', n) -> List['ProcessingUnit']:
        task_location: Location = task.getCurrentVehicle().getLocation()
        #pu_distance_list = [(pu, Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())) for pu in TaskMapper.pu_list]
        pu_distance_list = []

        pu: ProcessingUnit = None
        for pu in Store.pu_list:
            dist = Location.getDistanceInMetersBetween(task_location, pu.getParent().getLocation())
            item = (pu, dist)
            pu_distance_list.append(item)

        return sorted(pu_distance_list, key=lambda item: item[1])[:n]

    def showPUs():
        Store.log(Store.pu_list)
    
    def showTasks():
        pass

    def showStats():
        print("\n")
        print("-------------------- Stats ----------------------")
        # success
        print(f'{GREEN}Success tasks')
        t: Task = None
        ended_lambda = lambda t: t.execution_start_time != -1 and t.execution_end_time != -1
        ended_list = list(filter(ended_lambda, Store.all_tasks))
        for t in ended_list:
            print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop, {t.currentPU}')

        print(f'{YELLOW}Not complete tasks')
        started_not_ended_lambda = lambda t: t.execution_start_time != -1 and t.execution_end_time == -1
        started_not_ended_list = list(filter(started_not_ended_lambda, Store.all_tasks))
        for t in started_not_ended_list:
            print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop, {t.currentPU}')

        print(f'{RED}Not started tasks')
        not_started_lambda = lambda t: t.execution_start_time == -1 and t.execution_end_time == -1
        not_started_list = list(filter(not_started_lambda, Store.all_tasks))
        for t in not_started_list:
            print(f'{t} started at {t.execution_start_time} ended {t.execution_end_time}, sched rounds {t.scheduler_rounds}, total {t.getFlop()}, remaining {t.remaining_flop} flop, {t.currentPU}')

        print(f'{GREEN}Success {len(ended_list)}  {YELLOW} Incomplete {len(started_not_ended_list)}  {RED} Not finished {len(not_started_list)} \n')

        for pu in Store.pu_list:
            pu.show_stats()

        print(f"{YELLOW}-------------------- Stats ----------------------")