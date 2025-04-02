import streamlit as st
import pandas as pd
import requests
from io import StringIO
import pandas as pd
import streamlit as st
import pydeck as pdk
from pydeck.types import String
import numpy as np

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

data['Species_new'] = data['Species'].apply(lambda x: 'Cat' if x == 'Cat' else ('Dog' if x == 'Dog' else 'Others'))

# create found variable
data['Returned'] = np.where(data['Outcome Type'].str.contains('Stray Reclaim'),1,0)

# Subset the data to dogs only
dogs = data[data['Species'] == 'Dog']

# Extract year from intake date
dogs['Year'] = pd.to_datetime(dogs['Intake Date']).dt.year

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

# Display PyDeck plot in Streamlit
st.subheader("Hexagon Plot of Not Returned Dogs")
st.pydeck_chart(r)
