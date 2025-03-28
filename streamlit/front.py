import streamlit as st

st.set_page_config(
    page_title="Return-to-Owner Analysis",
    page_icon=":world_map:️",
    layout="wide",
)

"# HSHV streamlit-app"

"""Intros"""

import streamlit as st
import pandas as pd
import numpy as np
from data_script import get_rto

def remove_dupes(df):
    # need preprocessing that builds FullHSHVData2 
    """
    Removes duplicate records and non-granular addresses from the DataFrame.

    Parameters:
    df (pd.DataFrame): Input DataFrame containing animal data.

    Returns:
    pd.DataFrame: DataFrame with duplicates and non-granular addresses removed.
    """
    # Identify rows with missing zip codes
    df['address_no_zipcode'] = ~df['address_google'].str.contains(r'\b\d{5}\b', regex=True, na=False)

    # Identify rows with non-granular addresses
    granular_keywords = r'Ave|Rd|Dr|Trail|St|Pkwy|&|Park|Lake'
    df['no_full_address'] = ~df['address_google'].str.contains(granular_keywords, regex=True, na=False)

    # Filter out rows with missing zip codes and non-granular addresses
    non_granular_indices = df[(df['address_no_zipcode']) & (df['no_full_address'])].index
    df = df.drop(non_granular_indices)

    # Drop temporary columns used for filtering
    df = df.drop(columns=['address_no_zipcode', 'no_full_address'], errors='ignore')

    # Remove duplicates based on specific columns
    dup_factors = ['Intake Date', 'Species', 'Primary Breed', 'Location Found', 'Returned to Address']
    df = df.drop_duplicates(subset=dup_factors, keep='first').reset_index(drop=True)

    return df


def get_rto(df):
    # remove dupes
    df = remove_dupes(df)
    df['Returned'] = np.where(df['Outcome Type'].str.contains('Stray Reclaim'),1,0)
    # set index for ease to get duplicates
    df = df.set_index("Animal #")
    # convert to datetime
    df['Outcome Date'] = pd.to_datetime(df['Outcome Date'])
    df['Intake Date'] = pd.to_datetime(df['Intake Date'])
    df['intake_month'] = df['Intake Date'].dt.month
    df['YearMonth'] = df['Intake Date'].dt.strftime('%Y-%m')

    df_dog = df[df.Species=='Dog']
    df_dog = df_dog.groupby('YearMonth').agg({'Returned':['sum','count']})

    df_dog['rto_rate'] = df_dog['Returned']['sum']/df_dog['Returned']['count']*100.0

    df_dog = df_dog.reset_index()
    df_dog['year'] = pd.to_datetime(df_dog['YearMonth']).dt.year
    df_dog.columns = ['YearMonth','Returned', 'Total', 'rto_rate', 'year']
    dog_yearly = df_dog.groupby('year').agg({'Returned':'sum' ,'Total':'sum'})
    dog_yearly['rto'] = 100.0*dog_yearly.Returned/dog_yearly.Total

    return dog_yearly

# Streamlit app
st.title("Return-to-Owner (RTO) Analysis")

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

        # Plot the RTO rate
        st.subheader("RTO Rate Over Time")
        st.line_chart(rto_data['rto'])
    else:
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
else:
    st.info("Please upload a CSV file to begin.")
