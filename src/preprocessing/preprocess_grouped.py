import os
import sys
import time
import numpy as np
import pandas as pd
import src.constants.constants as constants


# Main function that splits provided data into day '.tsv' files
def preprocessing(result_folder, verbose):
    data_new_list = os.listdir(constants.data_folder)

    for elem in sorted(data_new_list):
        elem_path = os.path.join(constants.data_folder, elem)
        print(elem_path)
        data = prep_single_file(elem_path)
        time_start = time.time()

        # Iterate through all the days
        for day_timestamp, day_df in list(data.groupby(['day'])):
            file_path = get_f_name(day_timestamp, result_folder)
            flag = False

            if os.path.isfile(file_path) and verbose:
                lines = sum(1 for line in open(file_path))
                flag = True
                print('file_path:', file_path, 'lines before:', lines, end=' ')

            # Append new data to a file
            with open(file_path, 'a') as f:
                day_cols_sliced = day_df[
                    ['user', 'latitude', 'longitude', 'occured_at']]
                day_cols_sliced.to_csv(f, header=False, index=False, sep='\t')

            if flag and verbose:
                lines_after = sum(1 for line in open(file_path))
                print('lines after:', lines_after)

        print(elem_path, 'finished: %.2f s\n' % (time.time() - time_start))


# Prepare single file (from the ones provided) before grouping
def prep_single_file(file_path):
    data = pd.read_csv(file_path, delimiter=',',
                       dtype=constants.dtypes_raw_grouped)

    # Convert to timestamp
    data['occured_at'] = pd.to_datetime(data['occured_at'], errors='coerce')

    # Drop data that didn't convert well to timestamp
    print('Amount dropped:', len(data.index[data['occured_at'].isnull()]))
    data.drop(data.index[data['occured_at'].isnull()], inplace=True)

    # Add day column for grouping purposes
    data['day'] = data.occured_at.dt.floor('d')

    # Convert date to unix epoch
    data.loc[:, 'occured_at'] = data['occured_at'].values.astype(
        np.int64) // 10 ** 6

    # Check for any null values
    res_for_null = data.isnull().values.any()
    if res_for_null:
        sys.exit('Null data encountered')
    else:
        print('No null fields found')

    return data


# Get file path from timestamp
def get_f_name(timestamp, res_folder):
    f_name = timestamp.strftime("%Y%m%d") + '.tsv'
    f_path = os.path.join(res_folder, f_name)

    return f_path
