import numpy as np
import folium
from folium.plugins import HeatMap

# create map
data = (np.random.normal(size=(100, 3)) *
        np.array([[1, 1, 1]]) +
        np.array([[48, 5, 1]])).tolist()
folium_map = folium.Map([48., 5.], tiles='stamentoner', zoom_start=6)
HeatMap(data).add_to(folium_map)

# this won't work:
folium_map
folium_map.render()