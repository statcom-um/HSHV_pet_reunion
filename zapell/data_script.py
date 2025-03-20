import pandas as pd
import googlemaps

def get_google_maps_data(df, API_KEY=''):
    """
    Fetches corrected latitude, longitude, and addresses from Google Maps API for incorrect coordinates.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data with incorrect coordinates.
    API_KEY (str): Google Maps API key.

    Returns:
    pd.DataFrame: DataFrame with incorrect latitude, longitude, and addresses.
    """
    gmaps = googlemaps.Client(key=API_KEY)
    condition_1 = ~df['address_google'].str.contains('MI|Michigan', na=False)
    condition_2 = df['address_google'] == 'Michigan, USA'
    incorrect_coords_df = df[condition_1 | condition_2].copy()

    latitudes = []
    longitudes = []
    addresses = []

    # Iterate over each row in the DataFrame to get geocode data
    for index, row in incorrect_coords_df.iterrows():
        address = f"{row['Location Found']}, {row['Jurisdiction In']}, MI, USA"
        try:
            geocode_result = gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                latitudes.append(location['lat'])
                longitudes.append(location['lng'])
                addresses.append(geocode_result[0]['formatted_address'])
            else:
                latitudes.append(None)
                longitudes.append(None)
                addresses.append(None)
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
            latitudes.append(None)
            longitudes.append(None)
            addresses.append(None)

    incorrect_coords_df.loc[:, 'Latitude'] = latitudes
    incorrect_coords_df.loc[:, 'Longitude'] = longitudes
    incorrect_coords_df.loc[:, 'google_address_corrected'] = addresses

    return incorrect_coords_df


def process_data(csv_file='', API_KEY=''):
    """
    Processes the data from a CSV file, corrects coordinates using Google Maps API, and filters the data.

    Parameters:
    csv_file (str): Path to the CSV file containing the data.
    API_KEY (str): Google Maps API key.

    Returns:
    pd.DataFrame: Processed DataFrame with corrected coordinates and filtered data.
    """
    df = pd.read_csv(csv_file)
    #Rewrite the addresses so they are more interpretable by GeocodeAPI
    df['Jurisdiction In'] = df['Jurisdiction In'].replace(r'^WC-', '', regex=True)  # Remove WC-
    df['Jurisdiction In'] = df['Jurisdiction In'].replace(r'\s+(Twp|City)$', '', regex=True)
    df['Location Found'] = df['Location Found'].replace('/', ' and ', regex=True)

    # Get latitude and longitutde for each address
    df[['lon', 'lat']] = df['pnt'].str.split(', ', expand=True)
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')  
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

    # Change Incorrect Coordinates and Addresses
    incorrect_coords_df = get_google_maps_data(df, API_KEY)
    df.loc[incorrect_coords_df.index, 'lat'] = incorrect_coords_df['Latitude']
    df.loc[incorrect_coords_df.index, 'lon'] = incorrect_coords_df['Longitude']
    df.loc[incorrect_coords_df.index, 'address_google'] = incorrect_coords_df['google_address_corrected']   

    df['pnt'] = df['lon'].astype(str) + ', ' + df['lat'].astype(str)

    df[df['address_google'] == 'Michigan, USA']

    # Remove animals found at HSHV
    # Remove Out of State Observations
    df = df[~df['Location Found'].str.contains('HSHV', na=False)]
    df = df[df['address_google'].str.contains('MI', na=False)]    

    return df


def get_rto(df):
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


