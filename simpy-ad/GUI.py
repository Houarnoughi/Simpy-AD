import folium
import pandas as pd
from IPython.display import display, IFrame


franchises = pd.read_csv('../data/locations')

# view the dataset

print(franchises.head())

center = [-0.023559, 37.9061928]

map_kenya = folium.Map(location=center, zoom_start=8)

for index, franchise in franchises.iterrows():
    location = [franchise['latitude'], franchise['longitude']]

    folium.Marker(location, popup=f'Address:{franchise["address"]}\n Type($):{franchise["type"]}').add_to(map_kenya)

# save map to html file

map_kenya.save('index.html')

display(IFrame('index.html', width=700, height=450))
