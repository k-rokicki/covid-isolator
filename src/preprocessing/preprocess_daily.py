import concurrent.futures
from datetime import datetime, timedelta
import decimal
import os
import numpy as np
import pandas as pd
from pytz import country_timezones
from ua_parser import user_agent_parser

import src.constants.constants as constants


def preprocess_geo_data_worker(data_chunk):
    indexes_to_drop = []

    for index, row in data_chunk.iterrows():
        if abs(decimal.Decimal(str(row.lat)).as_tuple().exponent) < 3 \
                or abs(decimal.Decimal(str(row.lon)).as_tuple().exponent) < 3:
            indexes_to_drop.append(index)

    data_chunk = data_chunk.drop(indexes_to_drop, axis=0)
    return data_chunk


# Basic geo-data filter - remove rows without all columns
def preprocess_geo_data(data):
    data = data.loc[data.timeStamp.notnull() & data.lat.notnull() & data.lon.notnull() &
                    (data.timeStamp != 0) & (data.lat != 0.0) & (data.lon != 0.0)]

    split_data = np.array_split(data, constants.num_workers)
    combined_data = data[0:0]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for filtered_data in executor.map(preprocess_geo_data_worker, split_data):
            combined_data = combined_data.append(filtered_data)

    return combined_data


def parse_user_agent(user_agent):
    if pd.isnull(user_agent):
        return "unknown os"
    try:
        parsed_string = user_agent_parser.ParseOS(user_agent)
        result_string = parsed_string['family']
        if parsed_string['major']:
            result_string += ' ' + parsed_string['major']
        if parsed_string['minor']:
            result_string += '.' + parsed_string['minor']
        if parsed_string['patch']:
            result_string += '.' + parsed_string['patch']
        return result_string
    except:
        return user_agent


def shorten_user_agent_worker(data_chunk):
    data_chunk['userAgent'] = data_chunk['userAgent'].apply(parse_user_agent)
    return data_chunk


# Get os and version from userAgent
def shorten_user_agent(data):
    split_data = np.array_split(data, constants.num_workers)
    combined_data = data[0:0]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for shortened_data in executor.map(shorten_user_agent_worker, split_data):
            combined_data = combined_data.append(shortened_data)

    return combined_data


def remove_single_worker(data_chunk):
    unique_user_id = data_chunk.groupby(['userId', 'lat', 'lon']).size().reset_index(name='size') \
                        .groupby('userId').filter(lambda row: row['size'].count() > 1) \
                        .userId.unique()
    return data_chunk.loc[data_chunk['userId'].isin(unique_user_id)]


# Ignore non-moving users
def remove_single(data):
    split_data = [country for _, country in data.groupby('country')]
    combined_data = data[0:0]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for shortened_data in executor.map(remove_single_worker, split_data):
            combined_data = combined_data.append(shortened_data)

    return combined_data


# Read data from file and filter it
def read_data(file_path, preprocess_function, ignore_single):
    data = pd.read_csv(file_path, sep='\t', dtype=constants.dtypes_raw_daily,
                       header=None, names=constants.columns_names_daily,
                       usecols=constants.columns_to_read_daily, error_bad_lines=False)

    # Remove not full rows and with not enough exact location
    data = preprocess_function(data)

    # Parse userAgent
    data = shorten_user_agent(data)

    # Ignore single records (non-moving user)
    if ignore_single:
        data = remove_single(data)

    return data


def time_split_function(data, num_of_intervals, date):
    start_time = pd.to_datetime(date)
    end_time = pd.to_datetime(date) + pd.Timedelta('1 days')

    range_ = pd.date_range(start=start_time, end=end_time,
                           periods=(num_of_intervals + 1)).values
    group_by = pd.cut(pd.to_datetime(data['timeStamp'], unit='ms'), range_)

    data.loc[:, 'group'] = data.groupby([group_by]).ngroup()
    return data


# Ignore duplicates of records within single interval
def group_users_in_intervals(data, date):
    data_time_grouped = time_split_function(data, constants.num_intervals, date)
    data_time_grouped[['lat_rounded', 'lon_rounded']] = data_time_grouped[['lat', 'lon']].round(4)
    data_time_grouped.drop_duplicates(['userId', 'group', 'lat_rounded', 'lon_rounded'],
                                      inplace=True)

    return data_time_grouped.drop(['group', 'lat_rounded', 'lon_rounded'], axis='columns')


# Save records from previous day
def save_previous_day(path, date, countries):
    for index, country in enumerate(countries):
        curr_day = datetime.strptime(date, '%Y%m%d').date()
        prev_day = curr_day - timedelta(days=1)

        prev_day_file = prev_day.strftime('%Y%m%d')

        midnight_local = pd.to_datetime(date).timestamp() * 1000

        country_temp = country[1].loc[country[1]['timeStamp'] < midnight_local]
        temp = list(countries[index])
        temp[1] = country[1].loc[country[1]['timeStamp'] >= midnight_local]
        countries[index] = tuple(temp)

        country_temp.to_csv(os.path.join(path, country[0], prev_day_file + '.tsv'),
                            mode='a+', header=None, columns=constants.columns_to_save_daily,
                            index=False, sep='\t')

    return countries


# Save records from following day
def save_next_day(path, date, countries):
    for index, country in enumerate(countries):
        curr_day = datetime.strptime(date, '%Y%m%d').date()
        next_day = curr_day + timedelta(days=1)

        next_day_file = next_day.strftime('%Y%m%d')

        midnight_local = pd.to_datetime(next_day_file).timestamp() * 1000

        country_temp = country[1].loc[country[1]['timeStamp'] >= midnight_local]
        temp = list(countries[index])
        temp[1] = country[1].loc[country[1]['timeStamp'] < midnight_local]
        countries[index] = tuple(temp)

        country_temp.to_csv(os.path.join(path, country[0], next_day_file + '.tsv'),
                            mode='w', header=None, columns=constants.columns_to_save_daily,
                            index=False, sep='\t')

    return countries


# Save data to files
def split_by_country(path, date, data):
    # Split data by country
    countries = [(country, frame) for country, frame in data.groupby('country')]

    # Convert timezones for timeStamps
    for index, country in enumerate(countries):
        country_code = country_timezones(country[0])[0]
        data = group_users_in_intervals(country[1], date)
        data['timeStamp'] = pd.to_datetime(data['timeStamp'].astype(str), utc=True, unit='ms') \
                                .dt.tz_convert(tz=country_code).dt.tz_localize(None) \
                                .values.astype(np.int64) // 10 ** 6
        countries[index] = (country[0], data)

    # Append data from previous day into proper file
    countries = save_previous_day(path, date, countries)

    # Create file for next day
    countries = save_next_day(path, date, countries)

    # Save splitted data
    for country in countries:
        country[1].to_csv(os.path.join(path, country[0], date + '.tsv'),
                          columns=constants.columns_to_save_daily, header=None,
                          index=False, sep='\t', mode='a')


def preprocessing(day, ignore_single, result_folder):
    for file in os.scandir(constants.data_folder):
        if day in file.name:
            file_name = file.name
            break

    # Read and filter data
    data = read_data(os.path.join(constants.data_folder, file_name),
                     preprocess_geo_data, ignore_single)

    # Get date from file's name
    date = os.path.splitext(file_name)[0][-8:]

    # Save data from each country to separate directories
    split_by_country(result_folder, date, data)
