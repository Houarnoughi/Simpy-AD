import simpy

'''SimPy is a discrete-event simulation library. 
The behavior of active components (like vehicles, customers or messages) is modeled with processes. 
All processes live in an environment. 
They interact with the environment and with each other via events.

Processes are described by simple Python generators. 
You can call them process function or process method, depending on whether it is a normal function or method of a class. 
During their lifetime, they create events and yield them in order to wait for them to be triggered.

When a process yields an event, the process gets suspended. 
SimPy resumes the process, when the event occurs (we say that the event is triggered). 
Multiple processes can wait for the same event. 
SimPy resumes them in the same order in which they yielded that event.'''


def clock(env, name, tick):
    while True:
        print(name, env.now)
        # An important event type is the Timeout.
        # Events of this type are triggered after a certain amount of (simulated) time has passed.
        # They allow a process to sleep (or hold its state) for the given time.
        # A Timeout and all other events can be created by calling
        # the appropriate method of the Environment that the process lives in (Environment.timeout() for example).
        yield env.timeout(tick)


def car(env):
    while True:
        print('Start parking at %d' % env.now)
        parking_duration = 5
        yield env.timeout(parking_duration)

        print('Start driving at %d' % env.now)
        trip_duration = 2
        yield env.timeout(trip_duration)


def main1():
    env = simpy.Environment()
    env.process(clock(env, 'fast', 0.0016))
    env.process(clock(env, 'slow', 2))
    env.run(until=5)


def main2():
    env = simpy.Environment()
    env.process(car(env))
    env.run(until=15)


if __name__ == "__main__":
    # main1()
    main2()