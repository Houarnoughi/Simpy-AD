"""
Static class that holds Simulation's that keeps track of
    - all PUs
    -  all Tasks
"""
from Colors import END, GREEN, YELLOW, RED, BLUE
from typing import List, TYPE_CHECKING
from Location import Location
import random
import config
import os

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
    vehicle_list = []
    rsu_list = []
    datacenter_list = []

    all_tasks = []
    tasks_to_execute = []
    pu_list = []

    # TaskMapper sends tuple 
    #   task
    #   taskPu props
    #   pu
    task_pu_props = []

    # list of TaskMapperNet inputs dict(task, pu)
    input_list = []

    # lambda expressions to filter tasks
    success_lambda = lambda t: t.isStarted() and t.isFinished() and t.isFinishedBeforeDeadline()
    started_failed_lambda = lambda t: (t.isStarted() and t.isFinished()) and not t.isFinishedBeforeDeadline()
    started_not_finished_lambda = lambda t: t.isStarted() and not t.isFinished()
    not_started_lambda = lambda t: not t.isStarted()

    def log(message):
        print(f'{GREEN}[Store] {message} {END}')

    # FIFO
    def getTask() -> 'Task':
        return Store.tasks_to_execute.pop(0)

    def addTask(task: 'Task'):
        Store.tasks_to_execute.append(task)
        Store.all_tasks.append(task)
        
    def clearTasks():
        Store.tasks_to_execute.clear()

    def addPU(pu: 'ProcessingUnit'):
        Store.pu_list.append(pu)
    
    def getTasksToExecuteCount():
        #return len(Store.tasks_to_execute)
        return len(list(filter(Store.not_started_lambda, Store.all_tasks)))
    
    def getTotalTaskCount():
        return len(Store.all_tasks)

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

    def getStats():
        """
        returns a tuple of numbers of : success, incomplete, fail task
        """
        return None
    
    def getTaskList():
        if config.DATA_GENERATION_MODE:
            tasks = [t for t,_,_ in Store.task_pu_props]
            for t in tasks:
                pass
                print(t.new_id, t, t.execution_start_time, t.execution_end_time, t.deadline, t.getCurrentPU())
        else:
            tasks = Store.all_tasks
        return tasks

    def getSuccessTaskCount():
        tasks = Store.getTaskList()
        return len(list(filter(Store.success_lambda, tasks)))

    def getStartedFailedTaskCount():
        tasks = Store.getTaskList()
        return len(list(filter(Store.started_failed_lambda, tasks)))

    def getStartedNotFinishedTaskCount():
        tasks = Store.getTaskList()
        return len(list(filter(Store.started_not_finished_lambda, tasks)))

    def getNotStartedTaskCount():
        tasks = Store.getTaskList()
        return len(list(filter(Store.not_started_lambda, tasks)))

    # export tasks
    def export():

        if not Store.task_pu_props:
            print("Store input list is empty")
            return

        if not os.path.exists(config.OUT_FILE_PATH):
            with open(config.OUT_FILE_PATH, "w") as f:
                pass

        for i, (task, data, pu) in enumerate(Store.task_pu_props):
            if task.isStarted() and task.isFinished() and task.isFinishedBeforeDeadline():
                data["label"] = 1
            else:
                data["label"] = 0

        # features
        with open(config.OUT_FILE_PATH, "w") as f:
            _, sample, _ = Store.task_pu_props[0]
            params = list(sample.keys())
            for param in params:
                f.write(f'{param}')
                f.write(',')
                # if param != params[-1]:
                #     f.write(',')
            f.write('\n')

            for task, input, pu in Store.task_pu_props:
                features = list(input.values())
                #print(features)
                for feature in features:

                    f.write(str(feature))
                    f.write(',')
                    # if feature != features[-1]:
                    #     f.write(',')
                f.write('\n')

    def showStats():
        print("\n")
        print("-------------------- Stats ----------------------")
        # success
        # print(f'{GREEN}Success tasks')

        if config.DATA_GENERATION_MODE:
            tasks = [t for t,_,_ in Store.task_pu_props]
            for t in tasks:
                pass
                #print(t.new_id, t, t.execution_start_time, t.execution_end_time, t.deadline, t.getCurrentPU())
        else:
            tasks = Store.all_tasks

        t: Task = None

        
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
        for pu in Store.pu_list:
            pu.show_stats()

        print(f'{GREEN}Success {len(success_list)}') 
        print(f'{YELLOW}After deadline {len(started_failed_list)}')  
        print(f'{BLUE}Not finished {len(started_not_finished_list)}') 
        print(f'{RED}Not started {len(not_started_list)}') 

        print(f"{YELLOW}-------------------- Stats ----------------------")

        #return len(ended_list), len(started_not_ended_list), len(not_started_list)