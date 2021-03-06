from Units import Units
import simpy
from Server import Server
from Vehicle import Vehicle
from TaskSchedulingPolicy import TaskSchedulingPolicy

'''
Benchmarks sources : https://developer.nvidia.com/embedded/jetson-modules 
and https://developer.nvidia.com/blog/nvidia-jetson-agx-xavier-32-teraops-ai-robotics/

'''


class ProcessingUnit(simpy.Resource):
    idx = 0
    name = ''

    def __init__(self, flops, memory, power, memory_bw, task_list,  scheduler: TaskSchedulingPolicy, env: simpy.Environment, capacity=2):
        super().__init__(env, capacity)
        self.name = 'PU-{0}'.format(ProcessingUnit.idx)
        ProcessingUnit.idx += 1

        self.flops = flops
        self.memory = memory
        self.power = power
        self.memory_bw = memory_bw
        self.task_list = []
        self.scheduler = scheduler
        self.setTaskList(task_list)
        self.env = env
        # self.proc = env.process(self.updateTaskListExecution())

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
            print('[INFO] ProcessingUnit-setTaskList: {0} submitted to {1}'.format(task.getTaskName(),
                                                                                   self.getPUName()))

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
            print('[INFO] ProcessingUnit-submitTask: {0} submitted to {1}'.format(task.getTaskName(),
                                                                                  self.getPUName()))
        else:
            print('[ERROR] ProcessingUnit-submitTask: {0} already assigned to {1}'.format(task.getTaskName(),
                                                                                          self.getPUName()))

    def executeTask(self, task):
        exec_time = self.getTaskExecutionTime(task) * 1000
        yield self.env.timeout(exec_time)

    def updateTaskListExecution(self, frames):
        new_task_list = self.getScheduler().getExecutionSequence(self.getTaskList())
        for frame in range(frames):
            for task in new_task_list:
                print('[LOG] Starting executing {0} on {1} at {2}'.format(task.getTaskName(), self.getPUName(),
                                                                          self.env.now))
                start = self.env.now
                yield self.env.process(self.executeTask(task))
                print('[LOG] Finishing executing {0} on {1} at {2}'.format(task.getTaskName(), self.getPUName(),
                                                                           self.env.now))
                stop = self.env.now
                task.updateTotalExecutionTime(stop-start)
                yield self.env.timeout(0)


class AGX(ProcessingUnit):
    currentVehicle = None
    idx = 0

    def __init__(self, task_list, scheduler: TaskSchedulingPolicy, env, capacity=1):
        name = 'AGX-{0}'.format(AGX.idx)
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
        name = 'TX2-{0}'.format(TX2.idx)
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
        name = 'TeslaV100-{0}'.format(TeslaV100.idx)
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
        name = 'DGXa100-{0}'.format(DGXa100.idx)
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
