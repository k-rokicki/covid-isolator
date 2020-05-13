import argparse
import os
import src.preprocessing.preprocess_daily as preprocess_daily
import src.preprocessing.preprocess_grouped as preprocess_grouped
import src.constants.constants as constants

def run_preprocessing(result_path, daily, ignore_single, verbose):
    if daily:
        for file in os.scandir(constants.data_folder):
            day = file.name[:-8]
            preprocess_daily.preprocessing(day, ignore_single, result_path)
    else:
        preprocess_grouped.preprocessing(os.path.join(result_path, 'PL'), verbose)


parser = argparse.ArgumentParser()

parser.add_argument('path',
                    help='Path to existing, empty directory, '
                         'where files will be generated'
                         '(default=' + constants.preprocessed_folder + ')',
                    default=constants.preprocessed_folder,
                    nargs='?')

parser.add_argument('-d',
                    '--daily',
                    help='Run daily preprocessing, (default=False)',
                    action='store_true',
                    default=False)

parser.add_argument('-i',
                    '--ignore-single',
                    help='Ignore non-moving users in daily preprocessing, '
                         '(default=False)',
                    action='store_true',
                    default=False)

parser.add_argument('-v',
                    '--verbose',
                    help='Will display extra runtime info (default=False)',
                    action="store_true",
                    default=False)

args = parser.parse_args()

if (args.ignore_single and not args.daily):
    parser.error('The --ignore-single (-i) argument requires the --daily (-d)')

if (args.verbose and args.daily):
    parser.error('The --verbose (-v) argument cannot be used with the --daily (-d)')

run_preprocessing(args.path, args.daily, args.ignore_single, args.verbose)
