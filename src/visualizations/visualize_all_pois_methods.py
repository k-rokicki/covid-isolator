import src.constants.constants as const

import numpy as np
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# Find first daily .json file in results dir and uses it's keys as poi list
# for visualizations
def get_poi_types(poi_results_folder):
    file_list = sorted(os.listdir(poi_results_folder))
    for day_filename in file_list:
        if day_filename.endswith('.json'):
            with open(os.path.join(poi_results_folder, day_filename)) as f:
                res = list(json.load(f)['poi_list'].keys())
                break
    return res


# Get first and last day (as strings) in given folder (will be poi results)
def get_border_days(poi_results_folder):
    dir_listing = sorted(os.listdir(poi_results_folder))
    filtered = list(filter(lambda file: file.endswith('.json'), dir_listing))

    first = filtered[0]
    last = filtered[-1]
    return first[:-5], last[:-5]


# Prepare dictionary from POIs to counts in days and hours (filled with zeros)
def make_poi_dir(poi_list, day_count, interval_count):
    res = {}

    for name in poi_list:
        res[name] = np.zeros([day_count, interval_count])

    return res


# Update poi_dir and daily_counts by information from given day
def update_daily(poi_dir, json_file, first_day, daily_counts):
    res_from_day = json.load(json_file)
    day_str = res_from_day['date']
    curr_idx = get_day_idx(first_day, day_str)

    daily_counts[curr_idx][0] = res_from_day['data_points_from_day']
    daily_counts[curr_idx][1] = res_from_day['total_count']

    for poi_name, arr in res_from_day['poi_list'].items():
        poi_dir[poi_name][curr_idx] = arr


# Takes two strings and returns day difference between them (used as idx in arr)
def get_day_idx(first, curr):
    d_first = datetime.strptime(first, "%Y%m%d")
    d_curr = datetime.strptime(curr, "%Y%m%d")
    return abs((d_curr - d_first).days)


# Read all jsons from given folder and return a dictionary with all information
# needed to make visualizations
def read_all_jsons(poi_results_folder):
    poi_list = get_poi_types(poi_results_folder)
    first_day, last_day = get_border_days(poi_results_folder)
    day_count = get_day_idx(first_day, last_day) + 1

    poi_counts = make_poi_dir(poi_list, day_count, const.num_intervals)
    daily_counts = np.zeros([day_count, 2])

    for day_filename in sorted(os.listdir(poi_results_folder)):
        if day_filename.endswith('.json'):
            with open(os.path.join(poi_results_folder, day_filename)) as f:
                update_daily(poi_counts, f, first_day, daily_counts)

    ret = {
        'first_day': first_day,
        'day_count': day_count,
        'daily_counts': daily_counts,
        'poi_counts': poi_counts
    }

    return ret


# Prep folders for saving visualizations
def visualize_prep(visualizations_folder,
                   grouping_results_dir_path):
    info = read_all_jsons(grouping_results_dir_path)

    for poi_name in info['poi_counts']:
        curr_dir = os.path.join(visualizations_folder,
                                poi_name.replace("/", "_"))
        if not os.path.exists(curr_dir):
            os.makedirs(curr_dir)


# Generates list of days for visualizations in %m-%d-%a format (%a - weekday)
def generate_list_of_days(first_day, num_days):
    first_date = datetime.strptime(first_day, "%Y%m%d")

    res = [(first_date + timedelta(i)).strftime("%m-%d-%a") for i in
           range(num_days)]

    return res


# Returns new, normalized daily_counts according to normalize_option
def normalize_daily_counts(info, counts_days, normalize_option):
    if normalize_option == 0:
        return counts_days

    res = []
    for idx in range(len(counts_days)):
        if normalize_option == 1:
            data_from_day_count = info['daily_counts'][idx][0]
            if data_from_day_count == 0:
                res.append(0.0)
            else:
                res.append((const.scale_to_daily / data_from_day_count)
                           * counts_days[idx])

        elif normalize_option == 2:
            in_all_pois = info['daily_counts'][idx][1]
            if in_all_pois == 0:
                res.append(0.0)
            else:
                res.append(counts_days[idx] / in_all_pois)
    return res


# Centralize counts_days around mean if centralize flag is set
def centralize_daily_counts(info, counts_days, centralize):
    if centralize:
        last_base_idx = get_day_idx(info['first_day'], const.base_final_day)
        base = np.mean(counts_days[:last_base_idx])
        return (counts_days - base) / base
    else:
        return counts_days


# Set labeling of parts of the visualization
def set_names_and_ylabel(poi_name, normalize_option, centralize):
    poi_name_replaced = poi_name.replace("/", "_")

    if normalize_option == 2:
        y_label = 'Share of total in %'
        plt_title = poi_name + ', share of total'
        file_name = poi_name_replaced + '_share_of_total'

    elif normalize_option == 1:
        y_label = 'Counts in POI, normalized'
        plt_title = poi_name + ', normalized'
        file_name = poi_name_replaced + '_normalized'

    else:
        y_label = 'Counts in POI'
        plt_title = poi_name
        file_name = poi_name_replaced

    if centralize:
        y_label += ', change to base in %'
        plt_title += ', change to base'
        file_name += '_change_to_base'

    plt.ylabel(y_label, size=16)
    return plt_title, file_name


# Add coronavirus information
def add_legend(info, bar_list):
    patch_list = []
    first_date = info['first_day']

    for color, label, date in const.coronavirus_info_arr:
        patch = mpatches.Patch(color=color, label=label)
        date_idx = get_day_idx(first_date, date)
        bar_list[date_idx].set_color(color)
        patch_list.append(patch)
    plt.legend(handles=patch_list, fontsize=13, loc=1)


# Change yticks to % where needed, for centralize add y-tick interval -> 10%
def set_y_ticks(centralize, normalize_option):
    if not centralize and normalize_option != 2:
        plt.yticks(size=15)
    else:
        ticks, _ = plt.yticks()
        plt.yticks(ticks, [round(tick * 100, 2) for tick in ticks], size=15)


# Make visualization for single POI
def visualize_single(info,                   # all info from jsons
                     poi_name,               # what POI to visualize
                     coronavirus_info=True,  # coronavirus restrictions timeline
                     normalize_option=0,     # normalize daily counts option:
                                             # 0 -> no normalization
                                             # 1 -> normalize to 1000 000 daily
                                             # 2 -> as percentage from all POIs
                     centralize=True,        # Centralize around daily mean
                     save_dir=None):         # path to save dir, if None, plot
    counts_days = np.sum(info['poi_counts'][poi_name], axis=1, dtype=np.int64)
    counts_days = normalize_daily_counts(info, counts_days, normalize_option)
    counts_days = centralize_daily_counts(info, counts_days, centralize)

    list_of_days = generate_list_of_days(info['first_day'], info['day_count'])

    plt.figure(figsize=(15, 10))

    plt_title, file_name = set_names_and_ylabel(poi_name,
                                                normalize_option,
                                                centralize)

    plt.xlabel('Date', size=16)
    plt.title(plt_title, size=21)

    barlist = plt.bar(list_of_days, counts_days)
    x_ticks = np.arange(0, info['day_count'], 2)
    plt.xticks(x_ticks, rotation=90, size=15)

    set_y_ticks(centralize, normalize_option)

    plt.grid(axis='y')

    if coronavirus_info:
        add_legend(info, barlist)

    if save_dir is None:
        plt.show()
    else:
        plt.savefig(os.path.join(save_dir, file_name + '.png'),
                    bbox_inches='tight')
        plt.close()


# Make all available visualizations
# save_dir_path -> path to directory where files will be saved
# grouping_results_dir_path -> path to dir with poi-grouping results
# corona_info -> Bool if add corona legend
# change_to_base -> String day representing end of base, empty for no base
# For example:
# save_dir_path = '/home/zpp/visualizations/poiGrouping'
# grouping_results_dir_path = '/home/zpp/results/poiGrouping/PL'
def visualize_all(grouping_results_dir_path,
                  save_dir_path,
                  corona_info,
                  change_to_base):
    visualize_prep(save_dir_path, grouping_results_dir_path)
    info = read_all_jsons(grouping_results_dir_path)

    for poi_name in info['poi_counts']:
        save_current_dir = os.path.join(save_dir_path,
                                        poi_name.replace("/", "_"))
        for norm_opt in range(3):
            visualize_single(info, poi_name, corona_info, norm_opt, False,
                             save_current_dir)

            if change_to_base:
                visualize_single(info, poi_name, corona_info, norm_opt, True,
                                 save_current_dir)
