"""
The car will now drive to a battery charging station (BCS) and request one of its two charging spots.
If both of these spots are currently in use, it waits until one of them becomes available again.
It then starts charging its battery and leaves the station afterwards:
"""

# Add simpy lib
import simpy


def car(env, name, bcs, driving_time, charge_duration):
    # Simulate driving to the bcs
    yield env.timeout(driving_time)

    # Request one of its charging spots
    print('%s arriving at %d' % (name, env.now))
    with bcs.request() as req:
        yield req

        # Charge the battery
        print('%s starting to charge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %d' % (name, env.now))


def main():
    env = simpy.Environment()
    bcs = simpy.Resource(env, capacity=2)
    for i in range(4):
        env.process(car(env, 'Car %d' % i, bcs, i * 2, 5))
    env.run()


if __name__ == "__main__":
    main()
