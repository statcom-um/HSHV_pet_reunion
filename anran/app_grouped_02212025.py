import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import pandas as pd

# Read the data
data = pd.read_csv(r'Data\final_noduplicates.csv')

# Convert latitude and longitude to float
data['lat'] = data['lat'].astype(float)
data['lon'] = data['lon'].astype(float)

# Categorize species
data['Species_new'] = data['Species'].apply(lambda x: 'Cat' if x == 'Cat' else ('Dog' if x == 'Dog' else 'Others'))

# Define marker colors
marker_colors = {'Cat': 'orange', 'Dog': 'blue', 'Others': 'green'}

# Initialize map
center_lat, center_lon = 42.30638684408865, -83.65495118815288
m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# Create feature groups
fg_cat = folium.FeatureGroup(name='Cat', show=False)  # Hidden by default
fg_dog = folium.FeatureGroup(name='Dog', show=True)  # Visible by default
fg_others = folium.FeatureGroup(name='Others', show=False)  # Hidden by default

# Create MarkerClusters inside FeatureGroups
mCluster_cat = MarkerCluster(name="Cat").add_to(fg_cat)
mCluster_dog = MarkerCluster(name="Dog").add_to(fg_dog)
mCluster_others = MarkerCluster(name="Others").add_to(fg_others)

# Function to get marker color
def get_marker_color(species):
    return marker_colors.get(species, 'gray')

# Add markers only to the MarkerCluster (NOT to the FeatureGroup separately)
for _, row in data.iterrows():
    species = row['Species_new']
    lat, lon = row['lat'], row['lon']
    
    marker = folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(color=get_marker_color(species)),
        popup=f"Species: {species}<br>Outcome: {row['Outcome Type']}<br>Gender: {row['Gender']}",
        tooltip=f"{species} - {row['Outcome Type']}"
    )

    # Add marker only to the respective MarkerCluster
    if species == 'Cat':
        mCluster_cat.add_child(marker)
    elif species == 'Dog':
        mCluster_dog.add_child(marker)
    else:
        mCluster_others.add_child(marker)

# Add feature groups to the map
m.add_child(fg_cat)
m.add_child(fg_dog)
m.add_child(fg_others)

# Add layer control
folium.LayerControl(collapsed=False).add_to(m)

# Render map in Streamlit
st_data = st_folium(m, width=725)
