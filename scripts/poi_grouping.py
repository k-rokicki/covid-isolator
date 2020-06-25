import argparse
import os
import src.poiGrouping.poi_grouping_daily as poi_grouping_daily
import src.constants.constants as constants


def run_poi_grouping(preprocessed_path, results_path, country,
                     closest, daily, filtered, single_day, verbose):
    input_path = os.path.join(preprocessed_path, country)
    output_path = os.path.join(results_path, country)

    if single_day:
        poi_grouping_daily.run_poi_grouping_daily(single_day, country, closest,
                                                  daily, filtered, verbose,
                                                  input_path, output_path)
    else:
        for file in os.scandir(input_path):
            day = os.path.splitext(file.name)[0]
            poi_grouping_daily.run_poi_grouping_daily(day, country, closest,
                                                      daily, filtered, verbose,
                                                      input_path, output_path)


parser = argparse.ArgumentParser()

parser.add_argument('preprocessed_path',
                    help='Path to preprocessing results directory, '
                         '(default=' + constants.preprocessed_folder + ')',
                    default=constants.preprocessed_folder,
                    nargs='?')

parser.add_argument('results_path',
                    help='Path to store grouping results, '
                         '(default=' + constants.results_folder + ')',
                    default=constants.results_folder,
                    nargs='?')

parser.add_argument('country',
                    help='Country to group data from, '
                         '(default=PL)',
                    default='PL',
                    nargs='?')

parser.add_argument('-d',
                    '--daily',
                    help='Run daily grouping, (default=False)',
                    action='store_true',
                    default=False)

parser.add_argument('-s',
                    '--single-day',
                    type=str,
                    help='Run grouping for single day, '
                         'should be passed in YYYYMMDD format')

parser.add_argument('-v',
                    '--verbose',
                    help='Will display extra runtime info, (default=False)',
                    action="store_true",
                    default=False)

args = parser.parse_args()

run_poi_grouping(args.preprocessed_path, args.results_path,
                 args.country, args.daily, args.single_day, args.verbose)
