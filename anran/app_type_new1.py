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
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Dictionary to store feature groups by year
    year_groups = {}

    # Create a separate FeatureGroup for missing dates
    missing_date_group = folium.FeatureGroup(name="Missing Date", show=True)
    missing_date_cluster = MarkerCluster().add_to(missing_date_group)
    
    # Loop through unique years and create a FeatureGroup + MarkerCluster for each
    for year in dog_data['Outcome_Year'].dropna().unique():
        year = int(year)
        year_groups[year] = folium.FeatureGroup(name=str(year), show=True)
        marker_cluster = MarkerCluster().add_to(year_groups[year])

        # Add markers to the corresponding cluster
        for _, row in dog_data[dog_data['Outcome_Year'] == year].iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=f"Species: {row['Species_new']}<br>Outcome: {row['Outcome Type']}<br>Gender: {row['Gender']}<br>Year: {year}",
                tooltip=f"{row['Species_new']} - {row['Outcome Type']} ({year})"
            ).add_to(marker_cluster)

    # Add markers with missing dates to their own cluster
    for _, row in dog_data[dog_data['Outcome_Year'].isna()].iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"Species: {row['Species_new']}<br>Outcome: {row['Outcome Type']}<br>Gender: {row['Gender']}<br>Year: Missing",
            tooltip=f"{row['Species_new']} - {row['Outcome Type']} (Missing Date)"
        ).add_to(missing_date_cluster)
    
    # Heatmaps
    heat_data_all = data[['lat', 'lon']].dropna().values.tolist()
    heatmap_all = folium.FeatureGroup(name="All Cases Heatmap")
    HeatMap(heat_data_all, radius=15).add_to(heatmap_all)
    heatmap_all.add_to(m)
    
    # Heatmap for pets returned
    df_returned = data[~data['Returned to Address'].isna()].copy()
    heat_data_returned = df_returned[['lat', 'lon']].dropna().values.tolist()
    returned_layer = folium.FeatureGroup(name="Pets Returned Heatmap")
    HeatMap(heat_data_returned, radius=15).add_to(returned_layer)
    returned_layer.add_to(m)
    
    # Heatmap for pets not returned
    df_not_returned = data[data['Returned to Address'].isna()].copy()
    heat_data_not_returned = df_not_returned[['lat', 'lon']].dropna().values.tolist()
    not_returned_layer = folium.FeatureGroup(name="Pets Not Returned Heatmap")
    HeatMap(heat_data_not_returned, radius=15).add_to(not_returned_layer)
    not_returned_layer.add_to(m)
    
    # Add feature groups to the map
    for year, fg in year_groups.items():
        m.add_child(fg)
    m.add_child(missing_date_group)

    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)

    # Render Folium map in Streamlit
    st_folium(m, width=700, height=500)

else:
    st.error("Data could not be loaded. Please check the source URL or your internet connection.")
