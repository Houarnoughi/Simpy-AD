import simpy
from Colors import END, GREEN, YELLOW
import random

env = simpy.Environment()

class Task:
    ID = 1
    def __init__(self, flop):
        self.flop = flop
        self.remaining_flop = flop
        self.id = Task.ID
        Task.ID += 1
    
    def __repr__(self) -> str:
        return f'Task [{self.id}, flop {self.flop}, remaining {self.remaining_flop}]'

class PU:
    def __init__(self, name, env, scheduler):
        self.flops = 100000
        self.scheduler = scheduler
        self.env = env
        self.name = name
        self.tasks =  list()
        self.process = self.env.process(self.run())

    def addTask(self, task):
        self.tasks.append(task)
        self.scheduler.addTaskInQueue(task)

    def getTaskExecutionTime(self, task):
        flops = self.flops
        return task.flop / flops

    def execute_task(self, task):
        print("------------------")
        print(f"{GREEN}{self.name} executing {task} at {self.env.now}, tasks={len(self.tasks)}")
        q = self.scheduler.quantum
        qty = q * self.flops

        # if have less to burn in 1 quantum
        if qty >= task.remaining_flop:
            # get needed quantum for remaining flop to be yielded
            current_quantum = task.remaining_flop/self.flops
            self.scheduler.current_quantum = current_quantum

            # task finished
            task.remaining_flop = 0

            print(f"quantum {current_quantum}")
            yield self.env.timeout(current_quantum) 
        else:
            remaining_flop = task.remaining_flop
            
            q = remaining_flop/self.flops
            print("quantum 0.01")

            task.remaining_flop -= qty

            yield self.env.timeout(q) 

    def run(self):
        while True:
            #print(f"{GREEN}{self.name} run at {self.env.now}, tasks={len(self.tasks)}")
            # scheduler update tasks
            #print(f"sched tasks {len(self.scheduler.task_list)}")
            try:
                task = self.scheduler.getNextTask()
                if task:
                    print(f'got task from schedulemr {task}')
                    yield self.env.process(self.execute_task(task))
                    print(f"{GREEN}{self.name} after exec {task} at {self.env.now}, tasks={len(self.tasks)}")

                    if task.remaining_flop > 0:
                        print(f"Back to scheduler {task}")
                        self.scheduler.addTaskInQueue(task)

                    #input('enter to continue')
                else:
                    yield self.env.timeout(0.0001)
            except Exception as e:
                yield self.env.timeout(0.0001)
            
class Car:
    def __init__(self, name, pu: PU, env):
        self.FPS = 2
        self.env = env
        self.pu = pu
        self.name = name
        self.process = self.env.process(self.run())

    def run(self):
        while True:
            print(f"{YELLOW}{self.name} run at {self.env.now}")
            for _ in range(self.FPS):
                for _ in range(2):

                    t = Task(flop=random.randint(2000, 3000))
                    self.pu.addTask(t)

            yield self.env.timeout(1)

from TaskSchedulingPolicy import RoundRobinSchedulingPolicy

pu = PU('PU 1', env, scheduler=RoundRobinSchedulingPolicy(0.01))
car = Car('CAR 1', pu, env)

env.run(until=2)