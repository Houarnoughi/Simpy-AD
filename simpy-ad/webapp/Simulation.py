from threading import Thread, Condition
from multiprocessing import Process
from time import sleep
"""
class Simulation(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        while True:
            sleep(1)
            print("run")

    def stop(self):
        self._stop_event.set()
"""
class Simulation(Process):
    def __init__(self):
        Process.__init__(self)

    def run(self):
        while True:
            sleep(1)
            print("run")

if __name__ == '__main__':
    s = Simulation()
    s.start()

    sleep(4)

    s.terminate()