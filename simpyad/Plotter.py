from turtle import color
import numpy as np
from collections import namedtuple
import random
from Store import Store
import matplotlib.pyplot as plt
import config
from Vehicle import Vehicle

class Plotter:
    def __init__(self, env) -> None:
        self.env = env
        #self.env.process(self.run())
        self.env.process(self.map())

    def map(self):
        
        plt.ion()
        plt.figure(dpi=150)  
        plt.axis([config.MIN_LAT, config.MAX_LAT, config.MIN_LONG, config.MAX_LONG])
        #plt.axis([1, 5, 1, 10])
        ax = plt.gca()
        #ax.set_xlim([config.MIN_LAT, config.MAX_LAT])
        #ax.set_ylim([config.MIN_LONG, config.MAX_LONG])
        plt.title("Position")
        plt.xlabel("Type")
        plt.ylabel("Vehicle position")

        while True:
            plt.clf()
            # draw RSU
            for rsu in Store.rsu_list:
                lat = rsu.getLocation().getLatitude() 
                long = rsu.getLocation().getLongitude() 
                plt.scatter(long, lat, color="green", s=100)
                plt.annotate(rsu.name, (long, lat))

            # draw vahicles
            for v in Store.vehicle_list:
                lat = v.getLocation().getLatitude() 
                long = v.getLocation().getLongitude() 
                plt.scatter(long, lat, color="red")

            plt.pause(0.00005)
            
            yield self.env.timeout(1)
            

    def run(self):
        plt.ion()
        plt.figure(dpi=150)  
        ax = plt.gca()
        #ax.set_xlim([0, config.SIM_TIME])
        #ax.set_ylim([0, 100000])
        plt.title("Tasks")
        plt.xlabel("Type")
        plt.ylabel("Task count")

        x = 0
        while True:
            x=x+1
            #plt.scatter(x, count)

            try:
                plt.bar("Success", Store.getSuccessTaskCount(), color='green')
                #plt.bar("Started Failed", Store.getStartedFailedTaskCount(), color='yellow')
                #plt.bar("Not finished", Store.getStartedNotFinishedTaskCount(), color='orange')
                #plt.bar("Not started", Store.getNotStartedTaskCount(), color='red')

                plt.pause(0.00005)
            except Exception as e:
                print(e)
                input()
                pass

            yield self.env.timeout(0.1)
