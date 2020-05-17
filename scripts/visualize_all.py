from src.visualizations.visualize_all_pois_methods import *
import shutil
import argparse


def clean_all_previous_vis():
    vis_dir = const.visualizations_folder

    try:
        shutil.rmtree(vis_dir, ignore_errors=True)
    except OSError:
        print('Error removing dir', vis_dir)
        pass

    if not os.path.exists(vis_dir):
        os.makedirs(vis_dir)


def visualize_all_configurations(corona_info,
                                 base_day):
    directory_elements = os.listdir(const.results_folder)

    for file_name in directory_elements:
        file_path = os.path.join(const.results_folder, file_name)
        vis_file_path = os.path.join(const.visualizations_folder, file_name)

        print('Working on:', file_path)
        visualize_all(file_path,
                      vis_file_path,
                      corona_info,
                      base_day)


parser = argparse.ArgumentParser(description='Make visualizations for all POIs,'
                                             ' all configs')

parser.add_argument('-i',
                    '--corona_info',
                    help='Add legend for days where there were '
                         'coronavirus-related events',
                    action="store_true",
                    default=False)

parser.add_argument('-b',
                    '--change_to_base',
                    help='This argument is day (in format %%Y%%m%%d) will be '
                         'used to calculate base value from initial days, '
                         'all data will be shown relative to base. Base value '
                         'is average of all days to base day (excluding it). '
                         'By default: ' + const.base_final_day +
                         ', pass "" to omit.',
                    default=const.base_final_day)

parser.add_argument('-c',
                    '--clean',
                    help='Clean visualizations dir before running',
                    action="store_true",
                    default=False)

args = parser.parse_args()

if args.clean:
    clean_all_previous_vis()

visualize_all_configurations(args.corona_info,
                             args.change_to_base)
