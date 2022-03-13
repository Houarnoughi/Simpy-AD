from Units import Units
import simpy
from Server import Server
import Vehicle
from TaskSchedulingPolicy import TaskSchedulingPolicy
from Colors import YELLOW, END
'''
Benchmarks sources : https://developer.nvidia.com/embedded/jetson-modules 
and https://developer.nvidia.com/blog/nvidia-jetson-agx-xavier-32-teraops-ai-robotics/

'''


class ProcessingUnit(simpy.Resource):
    idx = 0
    name = ''

    def __init__(self, flops, memory, power, memory_bw, task_list,  scheduler: TaskSchedulingPolicy, env: simpy.Environment, capacity=1):
        super().__init__(env, capacity)
        self.name = f'PU-{ProcessingUnit.idx}'
        ProcessingUnit.idx += 1

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

    def getTaskList(self):
        return self.task_list

    def setTaskList(self, task_list):
        for task in task_list:
            task.setCurrentPU(self)
            self.task_list.append(task)
            print(f'[INFO] ProcessingUnit-setTaskList: {task.getTaskName()} submitted to {self.getPUName()}')

    def getScheduler(self):
        return self.scheduler

    def setScheduler(self, scheduler: TaskSchedulingPolicy):
        self.scheduler = scheduler

    def getTaskLoadingTime(self, task):
        return task.getSize() / self.getMemoryBandwidth()

    def getTaskExecutionTime(self, task):
        flops = self.getFlops()
        if self.getScheduler().getParallel():
            flops = int(self.getFlops()/len(self.getTaskList()))
        return task.getFlop() / flops

    def getTaskEnergyConsumption(self, task):
        return self.getTaskExecutionTime(task) * self.getPower()

    def submitTask(self, task):
        if task not in self.getTaskList():
            task.setCurrentPU(self)
            self.task_list.append(task)
            self.executed_tasks += 1
            self.log(f'[PUnit][INFO] ProcessingUnit-submitTask: {task.getTaskName()} submitted to {self.getPUName()} at {self.env.now}')
        else:
            self.log(f'[PUnit][ERROR] ProcessingUnit-submitTask: {task.getTaskName()} already assigned to {self.getPUName()}')

    def removeTask(self, task):
        if task in self.task_list:
            self.task_list.remove(task)

    def executeTask(self, task):
        exec_time = self.getTaskExecutionTime(task) * 1000
        yield self.env.timeout(exec_time)
        
    def log(self, message):
        print(f"{YELLOW}{message}{END}")
    
    def show_stats(self):
        self.log(f"{self.name} Executed {self.executed_tasks} tasks")

    def updateTaskListExecution(self):
        while True:
            if len(self.getTaskList()) == 0:
                #self.log(f"[PUnit][LOG] {self.getPUName()} No More Tasks")
                yield self.env.timeout(1)

            new_task_list = self.scheduler.getExecutionSequence(self.task_list)
            #print("new task list", new_task_list)
            #for frame in range(frames):
            for task in new_task_list:
                self.log(f'[PUnit][INFO] Starting executing {task.getTaskName()} on {self.getPUName()} at {self.env.now}')
                start = self.env.now
                yield self.env.process(self.executeTask(task))
                self.log(f'[PUnit][INFO] Finishing executing {task.getTaskName()} on {self.getPUName()} at {self.env.now}')

                # get vehicle and check if it's still in PU activity zone
                # if vehicle is outside, we consider task failed
                # to do
                vehicle = task.currentVehicle
                self.log(f'[PUnit][INFO] tasks vehicle {vehicle}')

                self.removeTask(task)

                stop = self.env.now
                task.updateTotalExecutionTime(stop-start)
                yield self.env.timeout(1)
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
