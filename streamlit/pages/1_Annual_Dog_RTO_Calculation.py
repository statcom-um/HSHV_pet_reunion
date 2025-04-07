import streamlit as st
import pandas as pd
import numpy as np
from data_script import get_rto

# Streamlit app
st.title("Return-to-Owner (RTO) Dog Analysis")

st.text("TO USE: Upload a csv file with columns named Outcome Type, Animal #, Outcome Date, Intake Date, Species")
st.text("There can be other columns in the file but these 5 are required and names are case and space dependent")

st.text("add example csv file")
st.image("../RTO_csv_example.png", caption="Example CSV file with required columns")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Ensure required columns exist
    required_columns = ['Outcome Type', 'Animal #', 'Outcome Date', 'Intake Date', 'Species']
    if all(col in df.columns for col in required_columns):
        # Process the data using get_rto
        rto_data = get_rto(df)

        # Display the results
        st.subheader("Yearly RTO Data")
        st.dataframe(rto_data)
        
        # Reset index and rename the column to 'year'
        rto_data = rto_data.reset_index().rename(columns={'index': 'year'})
        # Ensure 'year' column is a datetime year type
        rto_data['year'] = pd.to_datetime(rto_data['year'], format='%Y').dt.year
        
        # Plot the RTO rate
        st.subheader("RTO Rate Over Time")
        #st.line_chart(rto_data['rto'], x="year")
        #st.line_chart(rto_data, x='year', y='rto')
        st.line_chart(rto_data.set_index('year')['rto'])
    else:
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
else:
    st.info("Please upload a CSV file to begin.")
