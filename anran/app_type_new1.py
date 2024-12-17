import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
# read the data
import pandas as pd
data = pd.read_csv(r'Data\final_noduplicates.csv')
# latitude and longitude
data['lat'] = data['lat'].astype(float)
data['lon'] = data['lon'].astype(float)


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
    return marker_colors.get(species, 'gray')  # Default to gray if species not found

# Add custom markers for each row in the GeoDataFrame
for idx, row in data.iterrows():
    species = row['Species_new']  # Get the species
    lat = row['lat']  # Get latitude
    lon = row['lon']  # Get longitude
    
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
    # call to render Folium map in Streamlit
st_data = st_folium(m, width=725)