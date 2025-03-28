import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import pandas as pd
import requests
from io import StringIO

import pandas as pd
import streamlit as st
import pydeck as pdk
from pydeck.types import String
import numpy as np

# connect and read the data
def load_original_data():
    url = 'https://raw.githubusercontent.com/statcom-um/HSHV_pet_reunion/refs/heads/main/anran/Data/final_noduplicates.csv'
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Failed to load data from GitHub. Error: {e}")
        return None

# Load the data
data = load_original_data()

data['Species_new'] = data['Species'].apply(lambda x: 'Cat' if x == 'Cat' else ('Dog' if x == 'Dog' else 'Others'))

# Marker colors for each species
marker_colors = {
    'Cat': 'orange',
    'Dog': 'blue',
    'Others': 'green',
}
center_lat = data['lat'].mean()
center_lon = data['lon'].mean()


m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
mCluster_cat = MarkerCluster(name='Cat').add_to(m)
mCluster_dog = MarkerCluster(name='Dog').add_to(m)
mCluster_others = MarkerCluster(name='Others').add_to(m)
# Function to get color based on species
def get_marker_color(species):
    return marker_colors.get(species, 'gray')  

# Add custom markers for each row in the GeoDataFrame
for idx, row in data.iterrows():
    species = row['Species_new'] 
    lat = row['lat'] 
    lon = row['lon']  
    
    # Create a marker for each row, using the appropriate color
    marker = folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(color=get_marker_color(species)),  # Set marker color based on species
        popup=f"Species: {species}<br>Outcome: {row['Outcome Type']}<br>Gender: {row['Gender']}",  # Example of popup info
        tooltip=f"{species} - {row['Outcome Type']}"  # Example tooltip info
    )
    if species == 'Cat':
        mCluster_cat.add_child(marker)
    elif species == 'Dog':
        mCluster_dog.add_child(marker)
    elif species == 'Others':
        mCluster_others.add_child(marker) 

folium.LayerControl().add_to(m)
st_data = st_folium(m, width=725)

# create found variable
data['Returned'] = np.where(data['Outcome Type'].str.contains('Stray Reclaim'),1,0)

# Subset the data to dogs only
dogs = data[data['Species'] == 'Dog']

# Calculate overall return rate
return_rate = dogs['Returned'].mean()
return_rate

# Extract year from intake date
dogs['Year'] = pd.to_datetime(dogs['Intake Date']).dt.year

# Perform calculation per year
return_rate_per_year = dogs.groupby('Year')['Returned'].mean()

dogs['NotReturned'] = np.where(dogs['Outcome Type'].str.contains('Stray Reclaim'),0,1)

# Set up starting location and zoom level
view_state = pdk.ViewState(
    longitude=-83.6,
    latitude=42.3,
    zoom=8, 
    min_zoom=6,
    max_zoom=15,
    pitch=20.5, 
    bearing=-5)

hex_layer = pdk.Layer(
    'HexagonLayer',
    dogs,
    get_position='[lon, lat]',
    auto_highlight=True,
    elevation_scale=50,
    pickable=True,
    extruded=True, 
    radius=1000, 
    color_domain=[0.4, 0.99],
    opacity=0.5,
    get_color_weight='NotReturned',
    color_aggregation=String('MEAN'),
    coverage=1)

tooltip_html = {
    'html': '<b>Proportion Not Returned:</b> {colorValue} <br><b>Count:</b> {elevationValue}',
    'style': {
        'color': 'white'
    }
}

r = pdk.Deck(
    layers=[hex_layer],
    initial_view_state=view_state,
    tooltip=tooltip_html
)
r
# Display PyDeck plot in Streamlit
st.subheader("Hexagon Plot of Not Returned Dogs")
st.pydeck_chart(r)
