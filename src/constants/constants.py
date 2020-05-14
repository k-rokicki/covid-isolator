import numpy as np
import json
import os

data_folder = 'data'
header_path = data_folder + '/header.tsv'

results_folder = 'results'
preprocessed_folder = 'preprocessed/PL'

geo_json_path_original = 'geoJSON/original'
geo_json_path_filtered = 'geoJSON/filtered'

# Helper cutoff distance function
def cutoff_distances_dict(json_path):
    if os.path.isfile(json_path) and json_path.endswith('.json'):
        with open(json_path) as f:
            ret_dict = json.load(f)

        return ret_dict
    else:
        raise OSError('No .json file at specified location')


get_cutoff_distances_path = 'params/cutoff_distances.json'

cutoff_distances = cutoff_distances_dict(get_cutoff_distances_path)

one_degree_precision_in_m_at_equator = 111120

num_workers = 12

num_intervals = 24

column_names_raw = {}

dtypes_raw_daily = {
    'userId': 'Int64',
    'appBundle': str,
    'appName': str,
    'userAgent': str,
    'country': str,
    'city': str,
    'zipCode': str,
    'lat': np.float64,
    'lon': np.float64,
    'ipHash': 'Int64',
    'timeStamp': 'Int64'
}

dtypes_raw_grouped = {
    'user': 'Int64',
    'latitude': np.float64,
    'longitude': np.float64,
    'occured_at': str
}

dtypes_preprocessed_daily = {
    'userId': 'Int64',
    'OS': str,
    'lat': np.float64,
    'lon': np.float64,
    'timeStamp': 'Int64'
}

dtypes_preprocessed_grouped = {
    'userId': 'Int64',
    'lat': np.float64,
    'lon': np.float64,
    'timeStamp': 'Int64'
}

column_names_preprocessed_daily = np.array(['userId', 'OS', 'lat', 'lon',
                                      'timeStamp'], dtype='<U9')

column_names_preprocessed_grouped = np.array(['userId', 'lat', 'lon',
                                      'timeStamp'], dtype='<U9')


# Constants mostly for visualizations
base_final_day = '20200304'

coronavirus_info_arr = [('green', 'First infection in Poland', base_final_day),
                        ('yellow', 'All schools are closed', '20200316'),
                        ('orange', 'Movement restrictions', '20200325'),
                        ('red', 'Parks, forests and beaches closed, '
                         '\nrestrictions to number of people \nin shops',
                         '20200401')]

# What to scale all daily counts to (for normalization)
scale_to_daily = 1000000

# Constants for poi filtering
schools = ["Szkoła Podstawowa", "Gimnazjum", "Liceum", "LO",
            "Zespół Szkół", "ZS", "Technikum", "Zespół Szkolno-Przedszkolny"]
