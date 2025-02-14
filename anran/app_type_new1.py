import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import pandas as pd

# connect and read the data
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

    # Convert latitude and longitude to float
    data['lat'] = data['lat'].astype(float)
    data['lon'] = data['lon'].astype(float)
    
    # Filter only dog data
    data['Species_new'] = data['Species'].apply(lambda x: 'Cat' if x == 'Cat' else ('Dog' if x == 'Dog' else 'Others'))
    dog_data = data.loc[data['Species_new'] == 'Dog']
    
    # Define center coordinates (HSHV address)
    center_lat = 42.30638684408865
    center_lon = -83.65495118815288
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Add marker cluster for better visualization
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add custom markers for each dog
    for idx, row in dog_data.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"Species: {row['Species_new']}<br>Outcome: {row['Outcome Type']}<br>Gender: {row['Gender']}",
            tooltip=f"{row['Species_new']} - {row['Outcome Type']}"
        ).add_to(marker_cluster)  # Add marker to cluster
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Render Folium map in Streamlit
    st_folium(m, width=700, height=500)
else:
    st.error("Data could not be loaded. Please check the source URL or your internet connection.")
