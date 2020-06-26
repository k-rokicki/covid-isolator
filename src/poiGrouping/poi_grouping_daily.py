import src.constants.constants as constants

from shapely.geometry import shape, Point

import concurrent.futures
import pandas as pd
import numpy as np
import math
import json
import time
import os


date = None
country = None
only_closest_poi = False

dtypes_preprocessed = None
column_names_preprocessed = None

poi_shapes = {}


def get_list_of_files(dir_name, amenity):
    directory_items = os.listdir(dir_name)
    files = []
    for entry in directory_items:
        full_path = os.path.join(dir_name, entry)
        if os.path.isdir(full_path):
            files += get_list_of_files(full_path, (amenity + '.' + entry))
        else:
            files.append([full_path, amenity + '/' + entry[:-8]])
    return files


def get_trimmed_list_of_files(dir_name):
    ret = get_list_of_files(dir_name, '')
    res = []
    for [path, amenity] in ret:
        res.append([path, amenity[1:]])
    return res


def read_shapes(poi_geo_json_path):
    with open(poi_geo_json_path, 'r') as f:
        geo_json = json.load(f)

    res = []
    for elem in geo_json['features']:
        poi = shape(elem['geometry'])
        if poi.geom_type == 'MultiPolygon':
            for poly in poi:
                represent_point = poly.representative_point()
                res.append([represent_point.y, represent_point.x, poly])
        elif poi.geom_type == 'Polygon':
            represent_point = poi.representative_point()
            res.append([represent_point.y, represent_point.x, poi])
        elif poi.geom_type == 'Point':
            res.append([poi.y, poi.x, poi])
        else:
            pass
    return sorted(res, key=lambda x: x[0])


# Read file from path and return a DataFrame
def read_file(file_path):
    data = pd.read_csv(file_path, sep='\t', dtype=dtypes_preprocessed,
                       header=None, names=column_names_preprocessed,
                       error_bad_lines=False)
    data.loc[:, 'timeStamp'] = pd.to_datetime(data['timeStamp'].astype(str), unit='ms')
    return data


def time_split_function(data):
    global date

    start_time = pd.to_datetime(date)
    end_time = pd.to_datetime(date) + pd.Timedelta('1 days')

    range_ = pd.date_range(start=start_time, end=end_time,
                           periods=(constants.num_intervals + 1)).values

    group_by = pd.cut(data.timeStamp, range_)
    data.loc[:, 'group'] = data.groupby([group_by]).ngroup()

    return data[['lat', 'lon', 'group']]


def bin_search(data, val):
    lo, hi = 0, len(data) - 1
    best_ind = lo

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if data[mid] < val:
            lo = mid + 1
        elif data[mid] > val:
            hi = mid - 1
        else:
            best_ind = mid
            break

        if abs(data[mid] - val) <= abs(data[best_ind] - val):
            best_ind = mid

    return best_ind


def update_result_dictionary(result_dict, result):
    for poi_type, poi_counts in result.items():
        result_dict['poi_list'][poi_type] += poi_counts
        result_dict['total_count'] += sum(poi_counts)


def group_by_poi_worker(data_chunk):
    worker_result = {}
    for poi_type in poi_shapes.keys():
        worker_result[poi_type] = np.zeros(constants.num_intervals, dtype=np.int64)

    for (lat, lon, group) in data_chunk.values:
        point = Point(lon, lat)

        poi_types_dist = {}
        closest_dist = math.inf

        for curr_poi_type, curr_poi_shapes in poi_shapes.items():
            cutoff_distance = constants.cutoff_distances[curr_poi_type]

            lat_coords = [item[0] for item in curr_poi_shapes]

            lo_idx = bin_search(lat_coords, lat - cutoff_distance)
            hi_idx = bin_search(lat_coords, lat + cutoff_distance)

            closest_in_type = math.inf

            for i in range(lo_idx, hi_idx + 1):
                target_shape = curr_poi_shapes[i][2]
                dist = target_shape.distance(point)

                if dist <= cutoff_distance:
                    closest_in_type = min(closest_in_type, dist)

            if closest_in_type != math.inf:
                poi_types_dist[curr_poi_type] = closest_in_type
                closest_dist = min(closest_dist, closest_in_type)

        for poi_type, poi_dist in poi_types_dist.items():
            if only_closest_poi:
                if poi_dist == closest_dist:
                    worker_result[poi_type][int(group)] += 1
            else:
                worker_result[poi_type][int(group)] += 1

    return worker_result


def group_by_poi(_date, _country, filtered, verbose, preprocessed_path, save_path):
    global date, country, poi_shapes

    date = _date
    country = _country

    if verbose:
        print('Starting script for day ' + date)

    # Declare date folder path
    date_path = os.path.join(preprocessed_path, str(date) + '.tsv')

    # Make sure result directory exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Read from preprocessed
    if verbose:
        print('Loading data... ', end='', flush=True)
    start = time.time()
    data = read_file(date_path)
    end = time.time()
    if verbose:
        print('%.2f s' % (end - start))

    if data.empty:
        return

    # Group by time intervals (add time_group column and remove timestamp)
    data_time_grouped = time_split_function(data)

    # Final JSON object
    result_dict = {
        'date': date,
        'country': country,
        'data_points_from_day': len(data_time_grouped.index),
        'total_count': int(0),
        'num_of_intervals': int(constants.num_intervals),
        'poi_list': {}
    }

    # Get list of tuples poi_path and poi types
    if filtered:
        poi_list = get_trimmed_list_of_files(constants.geo_json_path_filtered)
    else:
        poi_list = get_trimmed_list_of_files(constants.geo_json_path_original)

    if verbose:
        print('Sorting POIs... ', end='', flush=True)
    start = time.time()

    for (poi_path, poi_types) in poi_list:
        # Get array of shapely objects with poi localizations
        poi_shapes[poi_types] = read_shapes(poi_path)
        result_dict['poi_list'][poi_types] = np.zeros(constants.num_intervals, dtype=np.int64)

    end = time.time()
    if verbose:
        print('%.2f s' % (end - start))

    split_data = np.array_split(data_time_grouped, constants.num_workers)

    if verbose:
        print('Classifying points... ', end='', flush=True)
    start = time.time()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(group_by_poi_worker, split_data):
            update_result_dictionary(result_dict, result)

    end = time.time()
    if verbose:
        print('%.2f s' % (end - start))

    for poi_type, poi_counts in result_dict['poi_list'].items():
        result_dict['poi_list'][poi_type] = poi_counts.tolist()

    result_dict['total_count'] = int(result_dict['total_count'])

    # Save JSON
    with open(os.path.join(save_path, (date + '.json')), 'w') as fp:
        json.dump(result_dict, fp)

    if verbose:
        print('Script finished successfully')
        print()


def run_poi_grouping_daily(day, _country, closest,
                           daily, filtered, verbose,
                           input_path, output_path):
    global only_closest_poi, dtypes_preprocessed, column_names_preprocessed

    if closest:
        only_closest_poi = True

    if daily:
        dtypes_preprocessed = constants.dtypes_preprocessed_daily
        column_names_preprocessed = constants.column_names_preprocessed_daily
    else:
        dtypes_preprocessed = constants.dtypes_preprocessed_grouped
        column_names_preprocessed = constants.column_names_preprocessed_grouped

    group_by_poi(day, _country, filtered, verbose, input_path, output_path)
