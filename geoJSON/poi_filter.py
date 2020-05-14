import src.constants.constants as constants
import json
import os

def filter_poi(directory, filename, school):
    with open(os.path.join(constants.geo_json_path_original, directory, filename), 'r') as f:
        geo_json = json.load(f)
        
    filtered = [feature for feature in geo_json['features'] if ('name' in feature['properties'])]
    if school:
        filtered = [feature for feature in filtered 
                    if any([school.lower() in feature['properties']['name'].lower() for school in constants.schools])]

    geo_json['features'] = filtered
    
    if not os.path.exists(os.path.join(constants.geo_json_path_filtered, directory)):
        os.makedirs(os.path.join(constants.geo_json_path_filtered, directory))

    with open(os.path.join(constants.geo_json_path_filtered, directory, filename), 'w', encoding='utf8') as f:
        json.dump(geo_json, f, ensure_ascii=False, indent=2)

for directory in os.scandir(constants.geo_json_path_original):
    for file in os.scandir(directory.path):
        filter_poi(directory.name, file.name, file.name.split('.')[0] == "school")
