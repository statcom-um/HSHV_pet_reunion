import folium
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap, FastMarkerCluster
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
    
    # Returned to Address (RTO)
    data['RTO'] = data['Returned to Address'].notna().astype(int)
    
    # Extract year from "Outcome Date"
    data['Outcome_Year'] = pd.to_datetime(data['Outcome Date'], errors='coerce').dt.year
    
    # Filter only dog data
    data['Species_new'] = data['Species'].apply(lambda x: 'Cat' if x == 'Cat' else ('Dog' if x == 'Dog' else 'Others'))
    dog_data = data.loc[data['Species_new'] == 'Dog']
    
    # Define center coordinates (HSHV address)
    center_lat = 42.30638684408865
    center_lon = -83.65495118815288
    
    # Set the callback function for marker color based on RTO
    callback = """\
    function (row) {
        var icon, marker;
        var color = row[2] === 1 ? "red" : "blue";  // If RTO = 1 -> red, else blue
        icon = L.AwesomeMarkers.icon({
            icon: "map-marker",
            markerColor: color
        });
        marker = L.marker(new L.LatLng(row[0], row[1]));
        marker.setIcon(icon);
        return marker;
    };
    """
    
    ### MAP 1: Original with Clustering (m_original)
    # Original Folium Map with markers
    m_original = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Dictionary to store feature groups by year
    year_groups = {}

    # Create a separate FeatureGroup for missing dates
    missing_date_group = folium.FeatureGroup(name="Missing Date", show=True)
    missing_date_data = dog_data[dog_data['Outcome_Year'].isna()][['lat', 'lon', 'RTO']].dropna().values.tolist()
    FastMarkerCluster(missing_date_data, callback=callback).add_to(missing_date_group)

    # Loop through unique years and create a FeatureGroup + MarkerCluster for each
    for year in dog_data['Outcome_Year'].dropna().unique():
        year = int(year)
        year_groups[year] = folium.FeatureGroup(name=str(year), show=True)
        year_data = dog_data[dog_data['Outcome_Year'] == year][['lat', 'lon', 'RTO']].dropna().values.tolist()
        
        FastMarkerCluster(year_data, callback=callback).add_to(year_groups[year])

     # Add feature groups to the map
    for year, fg in year_groups.items():
        m_original.add_child(fg)
    m_original.add_child(missing_date_group)

    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m_original)
    
    
    ### MAP 2: Without Clustering (m_noclust)
    m_noclust = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    year_groups_no_clust = {}

    missing_date_group_noclust = folium.FeatureGroup(name="Missing Date", show=True)
    for row in missing_date_data:
        color = "red" if row[2] == 1 else "blue"
        folium.CircleMarker(
            location=[row[0], row[1]],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            weight=1
        ).add_to(missing_date_group_noclust)

    for year in dog_data['Outcome_Year'].dropna().unique():
        year = int(year)
        year_groups_no_clust[year] = folium.FeatureGroup(name=str(year), show=True)
        year_data = dog_data[dog_data['Outcome_Year'] == year][['lat', 'lon', 'RTO']].dropna().values.tolist()
        
        for row in year_data:
            color = "red" if row[2] == 1 else "blue"
            folium.CircleMarker(
                location=[row[0], row[1]],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                weight=1
            ).add_to(year_groups_no_clust[year])

    for year, fg in year_groups_no_clust.items():
        m_noclust.add_child(fg)
    m_noclust.add_child(missing_date_group_noclust)
    folium.LayerControl(collapsed=False).add_to(m_noclust)

    # Render both maps in Streamlit
    st.write("### Heatmap of Pets Filter by Year (with clustering)")
    st.write("Red: Returned to Owner; Blue: Not Returned")   
    st_folium(m_original, width=700, height=500)

    st.write("### Heatmap of Pets Filter by Year (without clustering)")
    st.write("Red: Returned to Owner; Blue: Not Returned")
    st_folium(m_noclust, width=700, height=500)
    
               
    # Heatmap for pets returned
    m_returned = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    df_returned = data[~data['Returned to Address'].isna()].copy()
    heat_data_returned = df_returned[['lat', 'lon']].dropna().values.tolist()
    HeatMap(heat_data_returned, radius=15).add_to(m_returned)
    st.write("### Heatmap of Pets Returned")
    st_folium(m_returned, width=700, height=500)
    
    # Overall heatmap
    m_overall = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    heat_data_all = data[['lat', 'lon']].dropna().values.tolist()
    HeatMap(heat_data_all, radius=15).add_to(m_overall)
    st.write("### General Heatmap")
    st_folium(m_overall, width=700, height=500)

else:
    st.error("Data could not be loaded. Please check the source URL or your internet connection.")
