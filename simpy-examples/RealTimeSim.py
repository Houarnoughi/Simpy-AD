import time
import simpy
import simpy.rt


def example(env):
    start = time.perf_counter()
    yield env.timeout(1)
    end = time.perf_counter()
    print('Duration of one simulation time unit %.2fs' % (end - start))


def main1():
    env = simpy.Environment()
    proc = env.process(example(env))
    env.run(until=proc)


def main2():
    env = simpy.rt.RealtimeEnvironment(factor=0.01)
    proc = env.process(example(env))
    env.run(until=proc)


if __name__ == "__main__":
    main1()
    main2()

