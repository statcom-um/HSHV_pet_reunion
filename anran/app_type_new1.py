import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd

# Connect and read the data
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
    
    # Extract year from "Outcome Date"
    data['Outcome_Year'] = pd.to_datetime(data['Outcome Date'], errors='coerce').dt.year
    
    # Filter only dog data
    data['Species_new'] = data['Species'].apply(lambda x: 'Cat' if x == 'Cat' else ('Dog' if x == 'Dog' else 'Others'))
    dog_data = data.loc[data['Species_new'] == 'Dog']
    
    # Define center coordinates (HSHV address)
    center_lat = 42.30638684408865
    center_lon = -83.65495118815288
    
    # Heatmap for all cases
    m_all = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    heat_data_all = data[['lat', 'lon']].dropna().values.tolist()
    HeatMap(heat_data_all, radius=15).add_to(m_all)
    st.write("### All Cases Heatmap")
    st_folium(m_all, width=700, height=500)
    
    # Heatmap for pets returned
    m_returned = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    df_returned = data[~data['Returned to Address'].isna()].copy()
    heat_data_returned = df_returned[['lat', 'lon']].dropna().values.tolist()
    HeatMap(heat_data_returned, radius=15).add_to(m_returned)
    st.write("### Pets Returned Heatmap")
    st_folium(m_returned, width=700, height=500)
    
    # Heatmap for pets not returned
    m_not_returned = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    df_not_returned = data[data['Returned to Address'].isna()].copy()
    heat_data_not_returned = df_not_returned[['lat', 'lon']].dropna().values.tolist()
    HeatMap(heat_data_not_returned, radius=15).add_to(m_not_returned)
    st.write("### Pets Not Returned Heatmap")
    st_folium(m_not_returned, width=700, height=500)

else:
    st.error("Data could not be loaded. Please check the source URL or your internet connection.")
