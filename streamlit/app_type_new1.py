import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import pandas as pd
import requests
from io import StringIO

# Function to load data from GitHub URL
@st.cache_data
def load_original_data():
    url = 'https://raw.githubusercontent.com/statcom-um/HSHV_pet_reunion/refs/heads/main/anran/Data/final_noduplicates.csv'
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Failed to load data from GitHub. Error: {e}")
        return None

# Load the data
data = load_original_data()

# Check if data is loaded successfully
if data is not None:
    st.write("Data loaded successfully!")
    # st.write(data.head())  # Display the first few rows of the data

    # Add new species column
    data['Species_new'] = data['Species'].apply(lambda x: 'Cat' if x == 'Cat' else ('Dog' if x == 'Dog' else 'Others'))

    # Create a map
    m = folium.Map(location=[42.2808, -83.7430], zoom_start=12)

    # Create marker clusters
    mCluster_cat = MarkerCluster(name='Cats').add_to(m)
    mCluster_dog = MarkerCluster(name='Dogs').add_to(m)
    mCluster_others = MarkerCluster(name='Others').add_to(m)

    # Function to get marker color based on species
    def get_marker_color(species):
        if species == 'Cat':
            return 'blue'
        elif species == 'Dog':
            return 'green'
        else:
            return 'red'

    # Add custom markers for each row in the DataFrame
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
        else:
            mCluster_others.add_child(marker)

    # Display the map
    st_folium(m, width=700, height=500)
else:
    st.error("Data could not be loaded. Please check the source URL or your internet connection.")
