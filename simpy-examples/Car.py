"""
Waiting for a Process
---------------------

As it happens, a SimPy Process can be used like an event (technically, a process actually is an event).
If you yield it, you are resumed once the process has finished. Imagine a car-wash simulation where cars enter the
car-wash and wait for the washing process to finish.
Or an airport simulation where passengers have to wait until a security check finishes.

Lets assume that the car from our last example magically became an electric vehicle.
Electric vehicles usually take a lot of time charging their batteries after a trip.
They have to wait until their battery is charged before they can start driving again.

We can model this with an additional charge() process for our car.
Therefore, we refactor our car to be a class with two process methods:
run() (which is the original car() process function) and charge().

The run process is automatically started when Car is instantiated.
A new charge process is started every time the vehicle starts parking.
By yielding the Process instance that Environment.process() returns, the run process starts waiting for it to finish:
"""

import simpy

class TaskMapper:
    tasks = []
    def __init__(self, env) -> None:
        self.env = env
        # Start the run process every time an instance is created
        self.action = env.process(self.run())
    
    def run(self):
        while True:
            print(f"TaskMapper tasks {len(TaskMapper.tasks)}")
            
            yield self.env.timeout(1)



class Car(object):
    def __init__(self, env):
        self.env = env
        # Start the run process every time an instance is created
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('Start parking and charging at %d' % self.env.now)
            TaskMapper.tasks.append("task")
            charge_duration = 5
            # We yield the process that process() returns to wait for it ti finish
            yield self.env.process(self.charge(charge_duration))

            # The charge process has finished and we can start driving again
            print('Start driving at %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        yield self.env.timeout(duration)


class CarWithInterrupt(object):
    def __init__(self, env):
        self.env = env
        # Start the run process every time an instance is created
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('Start parking and charging at %d' % self.env.now)
            charge_duration = 5
            # We may get interrupted while charging the battery
            try:
                yield self.env.process(self.charge(charge_duration))
            except simpy.Interrupt:
                # When we receive an Interrupt, we stop charging and switch to the "driving" state
                print('Was interrupted. Hope the battery is full enough ...')

            # The charge process has finished and we can start driving again
            print('Start driving at %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        yield self.env.timeout(duration)


"""
The driver process has a reference to the car’s action process. After waiting for 3 time steps, it interrupts that process.

Interrupts are thrown into process functions as Interrupt exceptions that can (should) be handled by the interrupted process. 
The process can then decide what to do next (e.g., continuing to wait for the original event or yielding a new event):
"""


def driver(env, car):
    yield env.timeout(3)
    car.action.interrupt()


def main():
    env = simpy.Environment()
    mapper = TaskMapper(env)
    car1 = Car(env)
    car2 = Car(env)
    env.run(until=20)


def main2():
    env = simpy.Environment()
    car = CarWithInterrupt(env)
    env.process(driver(env, car))
    env.run(until=20)


if __name__ == "__main__":
    main()
