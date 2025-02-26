import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static


pd.read_csv(r'Data\final_noduplicates.csv')
final_noduplicates = load_data()

# Streamlit page configuration
st.set_page_config(page_title='Pet Return Heatmap', page_icon=':dog:')
st.title("Pet Return Heatmap")

# Create heatmaps
def create_heatmap(df, title):
    map_center = [df['lat'].mean(), df['lon'].mean()]
    m = folium.Map(location=map_center, zoom_start=10)
    heat_data = df[['lat', 'lon']].values.tolist()
    HeatMap(heat_data, radius=15).add_to(m)
    return m

# Sidebar filter
option = st.sidebar.radio("Select Heatmap Type:", ("All Pets", "Pets Returned", "Pets Not Returned"))

if option == "All Pets":
    st.subheader("Heatmap of All Reported Pets")
    heatmap = create_heatmap(final_noduplicates, "All Pets")
elif option == "Pets Returned":
    df_returned = final_noduplicates[~final_noduplicates['Returned to Address'].isna()]
    st.subheader("Heatmap of Pets That Were Returned")
    heatmap = create_heatmap(df_returned, "Pets Returned")
else:
    df_not_returned = final_noduplicates[final_noduplicates['Returned to Address'].isna()]
    st.subheader("Heatmap of Pets Not Returned")
    heatmap = create_heatmap(df_not_returned, "Pets Not Returned")

# Display map
folium_static(heatmap)
