from Units import Units
import simpy
from Server import Server
import Vehicle
from TaskSchedulingPolicy import TaskSchedulingPolicy, TaskScheduling
from Colors import YELLOW, END
from time import time
from TaskMapper import TaskMapper
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from Task import Task
'''
Benchmarks sources : https://developer.nvidia.com/embedded/jetson-modules 
and https://developer.nvidia.com/blog/nvidia-jetson-agx-xavier-32-teraops-ai-robotics/

'''

"""
PU's parent can be
    - Vehicle
    - RSU
    - DataCenter
"""
class ProcessingUnit(simpy.Resource):
    idx = 0
    name = ''

    def __init__(self, flops, memory, power, memory_bw, task_list: List['Task'], scheduler: TaskSchedulingPolicy, env: simpy.Environment, capacity=1):
        super().__init__(env, capacity)
        self.name = f'PU-{ProcessingUnit.idx}'
        ProcessingUnit.idx += 1

        self.parent = None
        self.flops = flops
        self.memory = memory
        self.power = power
        self.memory_bw = memory_bw
        self.task_list = []
        self.scheduler = scheduler
        self.setTaskList(task_list)
        self.env = env
        self.proc = env.process(self.updateTaskListExecution())

        self.executed_tasks = 0

    def getPUName(self):
        return self.name

    def setPuName(self, name):
        self.name = name

    def getFlops(self):
        return self.flops

    def setFlops(self, flops):
        self.flops = flops

    def getMemory(self):
        return self.memory

    def setMemory(self, memory):
        self.memory = memory

    def getPower(self):
        return self.power

    def setPower(self, power):
        self.power = power

    def getMemoryBandwidth(self):
        return self.memory_bw

    def setMemoryBandwidth(self, memory_bw):
        self.memory_bw = memory_bw

    def getTaskList(self) -> List['Task']:
        return self.task_list

    def setTaskList(self, task_list: List['Task']):
        task: Task = None
        for task in task_list:
            task.setCurrentPU(self)
            self.task_list.append(task)
            self.log(f'ProcessingUnit-setTaskList: {task.getTaskName()} submitted to {self.getPUName()}')

    def getScheduler(self) -> TaskScheduling:
        return self.scheduler

    def setScheduler(self, scheduler: TaskSchedulingPolicy):
        self.scheduler = scheduler

    def getTaskLoadingTime(self, task: 'Task'):
        return task.getSize() / self.getMemoryBandwidth()

    def getTaskExecutionTime(self, task: 'Task'):
        flops = self.getFlops()
        if self.getScheduler().getParallel():
            flops = int(self.getFlops()/len(self.getTaskList()))
        return task.getFlop() / flops

    def getTaskEnergyConsumption(self, task: 'Task'):
        return self.getTaskExecutionTime(task) * self.getPower()

    def submitTask(self, task: 'Task'):
        
        if task not in self.getTaskList():
            task.setCurrentPU(self)
            self.task_list.append(task)

            # add task to scheduler
            self.scheduler.addTaskInQueue(task)

            self.executed_tasks += 1
            self.log(f'submitTask: {task.getTaskName()} submitted to {self.getPUName()} at {self.env.now}')
        else:
            self.log(f'submitTask: {task.getTaskName()} already assigned to {self.getPUName()}')

    def removeTask(self, task):
        if task in self.task_list:
            self.task_list.remove(task)
    
    def getQuantumFlop(self):
        q = self.scheduler.quantum/1000
        return q * self.getFlops()

    def execute_task(self, task: 'Task'):
        self.log(f'execute_task: Scheduler {self.scheduler.__class__.__name__}')
        if hasattr(self.getScheduler(), 'quantum'):
            qty = self.getQuantumFlop()

            # if have less to burn in 1 quantum
            if qty >= task.remaining_flop:
                # get needed quantum for remaining flop to be yielded
                current_quantum = task.remaining_flop/self.flops
                # task finished
                task.remaining_flop = 0
                self.log(f'execute_task: Task {task} finished at {self.env.now}')
                self.log(f"execute_task: quantum {current_quantum}")
                yield self.env.timeout(current_quantum)
            # normal quantum execution
            else:
                self.log(f'execute_task: before burst task {task} remaining flop={task.remaining_flop}')
                task.remaining_flop -= qty
                self.log(f'execute_task:  after burst task {task} remaining flop={task.remaining_flop}')
                yield self.env.timeout(self.scheduler.quantum) 
        else:
            self.log("execute_task: No quantum")
            exec_time = self.getTaskExecutionTime(task) * 1000
            task.execution_start_time = time()
            # task finished
            task.remaining_flop = 0
            yield self.env.timeout(exec_time)
    
    def log(self, message):
        print(f"{YELLOW}[PU] {message}{END}")
    
    def show_stats(self):
        self.log(f"{self.name} Executed {self.executed_tasks} tasks")

    def setParent(self, parent):
        print(f"PU setParent called with {parent}")
        self.parent=parent
    
    def getParent(self):
        return self.parent

    def updateTaskListExecution(self):
        CYCLE = 0.001
        while True:
            #print(f"{GREEN}{self.name} run at {self.env.now}, tasks={len(self.tasks)}")
            # scheduler update tasks
            #print(f"sched tasks {len(self.scheduler.task_list)}")
            try:
                task = self.scheduler.getNextTask()
                if task:
                    self.log(f'got task from scheduler {task}')
                    yield self.env.process(self.execute_task(task))
                    self.log(f" after exec {task} at {self.env.now}, tasks={len(self.tasks)}")

                    if task.remaining_flop > 0:
                        self.log(f"Back to scheduler {task}")
                        self.scheduler.addTaskInQueue(task)

                    #input('enter to continue')
                else:
                    self.log(f'No Task Found. CYCLE at {self.env.now}')
                    yield self.env.timeout(CYCLE)
            except Exception as e:
                #self.log(f'CYCLE at {self.env.now}')
                yield self.env.timeout(CYCLE)


    def old_updateTaskListExecution(self):
        while True:
            #new_task_list = self.scheduler.getExecutionSequence(self.task_list)
            new_task_list = self.scheduler.getExecutionSequence()

            for task in new_task_list:
                self.log(f'Starting executing {task.getTaskName()} on {self.getPUName()} at {self.env.now}')
                start = self.env.now

                # To-do execute task according to scheduling policy
                # decrease flops and yield a scheduler's quantum
                print("BEFORE execute task")
                yield self.env.process(self.executeTask(task))
                print("AFTER execute task")
                task.execution_end_time = time()
                self.log(f'Finishing executing {task.getTaskName()} on {self.getPUName()} at {self.env.now}, took {task.getTotalExecutionTime()}')
                self.log(f'Task ended {task.execution_end_time}, deadline {task.deadline}, failed={task.isFailed()}')
                self.log(f'Total flops {task.getFlop()}, remaining {task.remaining_flop} ')
                # get vehicle and check if it's still in PU activity zone (actually RoadSideUnit's one)
                # if vehicle is outside, we consider task failed -> optimize model
                # to do
                
                vehicle = task.getCurrentVehicle()
                parent = self.parent
                location = parent.getLocation()

                if vehicle.name == parent.name:
                    print("on board")
                    pass
                self.log(f'Task from vehicle {vehicle} on Parent {parent}, location {location}')

                self.removeTask(task)
                """
                # if no more flops remaining
                if task.isDone():
                    self.removeTask(task)
                """
                # train step ?
                TaskMapper.optimize()

                # for later stats
                TaskMapper.all_tasks.append(task)

                stop = self.env.now
                task.updateTotalExecutionTime(stop-start)

                #yield self.env.timeout(1)

            yield self.env.timeout(1)

    def __repr__(self) -> str:
        return f"{self.name}"

class AGX(ProcessingUnit):
    currentVehicle = None
    idx = 0

    def __init__(self, task_list, scheduler: TaskSchedulingPolicy, env, capacity=1):
        name = f'AGX-{AGX.idx}'
        AGX.idx += 1
        flops = 11 * Units.tera
        memory = 32 * Units.giga
        power = 30  # 10W / 15W / 30W
        memory_bw = 137 * Units.giga
        super().__init__(flops, memory, power, memory_bw, task_list, scheduler, env, capacity)
        super().setPuName(name)

    def getCurrentVehicle(self):
        return self.currentVehicle

    def setCurrentCurrentVehicle(self, vehicle: Vehicle):
        self.currentVehicle = vehicle


class TX2(ProcessingUnit):
    currentVehicle = None
    idx = 0

    def __init__(self, task_list, scheduler: TaskSchedulingPolicy, env, capacity=1):
        name = f'TX2-{TX2.idx}'
        TX2.idx += 1
        flops = 1.33 * Units.tera
        memory = 8 * Units.giga
        power = 15  # 7.5W / 15W
        memory_bw = 59.7 * Units.giga
        super().__init__(flops, memory, power, memory_bw, task_list, scheduler, env, capacity)
        super().setPuName(name)

    def getCurrentVehicle(self):
        return self.currentVehicle

    def setCurrentCurrentVehicle(self, vehicle: Vehicle):
        self.currentVehicle = vehicle


# Values got from
# https://www.nvidia.com/fr-fr/data-center/tesla-v100/
class TeslaV100(ProcessingUnit):
    currentServer = None
    idx = 0

    def __init__(self, task_list, scheduler: TaskSchedulingPolicy, env, capacity=1):
        name = f'TeslaV100-{TeslaV100.idx}'
        TeslaV100.idx += 1
        flops = 112 * Units.tera
        memory = 32 * Units.giga
        power = 300
        memory_bw = 900 * Units.giga
        super().__init__(flops, memory, power, memory_bw, task_list, scheduler, env, capacity)
        super().setPuName(name)

    def getCurrentServer(self):
        return self.currentServer

    def setCurrentServer(self, server: Server):
        self.currentServer = server


# Values got from
# https://images.nvidia.com/aem-dam/Solutions/Data-Center/nvidia-dgx-a100-datasheet.pdf
class DGXa100(ProcessingUnit):
    currentServer = None
    idx = 0

    def __init__(self, task_list, scheduler: TaskSchedulingPolicy, env, capacity=1):
        name = f'DGXa100-{DGXa100.idx}'
        DGXa100.idx += 1
        flops = 5 * Units.peta
        memory = 320 * Units.giga
        power = 6.5 * Units.kilo
        memory_bw = 2 * Units.tera
        super().__init__(flops, memory, power, memory_bw, task_list, scheduler, env, capacity)
        super().setPuName(name)

    def getCurrentServer(self):
        return self.currentServer

    def setCurrentServer(self, server: Server):
        self.currentServer = server
