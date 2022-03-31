"""
Static class that holds Simulation's that keeps track of
    - all PUs
    -  all Tasks
"""
from Colors import END, GREEN
from typing import List, TYPE_CHECKING
from Location import Location
import random

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