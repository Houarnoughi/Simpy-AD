import numpy as np
from collections import namedtuple
import random
import matplotlib.pyplot as plt


Location = namedtuple('Location', ['lon','lat'])

va = Location(50.36328322047431, 3.5171747551323005)
lille = Location(50.63725143907785, 3.0702985651377745)

step = 10
deviation = 20

trip_lon = np.linspace(va.lon, lille.lon, step)
trip_lat = np.linspace(va.lat, lille.lat, step)

augm = lambda e: e + np.random.uniform(-1,1)/deviation
trip_lon = list(map(augm, trip_lon))
trip_lat = list(map(augm, trip_lat))

plt.figure(dpi=150)  

plt.scatter(*va)
plt.annotate("Va", (va.lon, va.lat))
plt.scatter(*lille)
plt.annotate("Lille", (lille.lon, lille.lat))

plt.plot(trip_lon,trip_lat,"go--",label='Trip',linestyle="dashed", markersize=2, linewidth=5)

plt.gca().invert_xaxis()
plt.gca().invert_yaxis()

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title(" Trip ")

plt.legend()
plt.show()