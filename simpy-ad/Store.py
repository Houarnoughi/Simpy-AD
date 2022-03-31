"""
Static class that holds Simulation's that keeps track of
    - all PUs
    -  all Tasks
"""
from Colors import END, GREEN
from typing import List
from Task import Task
from ProcessingUnit import ProcessingUnit

class Store:
    """
    Tasks are assingned to this class on runtime by Vehicles
    Pus are set at the beginning
    """
    task_list = []
    pu_list = []

    def _log(message):
        print(f'{GREEN}[Store] {message} {END}')

    def addTask(task: Task):
        Store.task_list.append(task)

    def addPU(pu: ProcessingUnit):
        Store.pu_list.append(pu)
    
    def showPUs():
        Store._log(Store.pu_list)
    
    def showTasks():
        pass

    def getTaskCount():
        return len(Store.task_list)

    def getPuCount():
        return len(Store.pu_list)