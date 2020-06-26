# covid-isolator

Tool for monitoring of human aggregates during quarantine using geolocation data

## Table of Contents


* [Getting started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Creating an environment](#creating-an-environment)
* [Preprocessing](#preprocessing)
  * [Adding data](#adding-data)
    * [Daily data](#daily-data)
    * [Grouped data](#grouped-data)
  * [Running preprocessing script](#running-preprocessing-script)
    * [Preprocessing parameters](#preprocessing-parameters)
* [Grouping](#grouping)
  * [geoJSON](#geojson)
  * [Cutoff distances](#cutoff-distances)
  * [Running grouping script](#running-grouping-script)
    * [Grouping parameters](#grouping-parameters)
* [Creating visualizations](#creating-visualizations)
  * [Visualizations parameters](#visualizations-parameters)
  * [Results description](#results-description)
* [Authors](#authors)

## Getting started

### Prerequisites

To run covid-isolator, you will need the newest version of Anaconda, available via the following link:

```
https://www.anaconda.com/products/individual
```

Download the installation script, make it executable and run it, e.g.

```
chmod +x Anaconda3-2020.02-Linux-x86_64.sh
./Anaconda3-2020.02-Linux-x86_64.sh
```

### Creating an environment

To create Anaconda environment with all nessesary packages, run:

```
conda env create -f environment.yml
```

This will create new environment named "covid-isolator". To activate it, run:

```
conda activate covid-isolator
```

All of the following instructions need to be executed with covid-isolator environment activated.

To deactivate environment, just run:

```
conda deactivate
```

### Folder initialization

In order to initialize default directories used throughout this project 
run `init.sh` script located in scripts folder. The directories created by this 
script are:
* **data** - input data should be placed here,
* **preprocessed** - preprocessing results by default will be stored here,
* **results** - grouping results will be stored here,
* **visualizations** - generated visualizations will be stored here.

If you want to use other directories instead of the ones provided, you will 
need to change appropriate paths in `src/constants/constants.py`

## Preprocessing

### Adding data

Before running preprocessing script add .tsv files to `data` directory. Data should be in one of the following formats: 

- #### Daily data

  Single file should contain data from one day (optionally from previous and following days) and all files should be named in "*YYYYMMDD" format.

  | **userId** | **appBundle** | **appName** | **userAgent** | **country** | **city** | **zipCode** | **lat** | **lon** | **ipHash** | **timestamp** |
  |   :---:    |     :---:     |    :---:    |     :---:     |    :---:    |  :---:   |    :---:    |  :---:  |  :---:  |    :---:   |      :---:    |
  | 888831757 | com.sample.app | Android App | User-Agent header | PL | Warsaw | 00-901 | 52.231586 | 21.007095 | -1893732788 | 1582594992769|
  |-474030351 | 381471012 | iOS App | User-Agent header | FR | Nantes | 44000 | 48.86131 | 2.33141 | 1572663506 | 1582594992687 |

  - **userId**: user identifier
  - **appBundle**: application identifier from Google Play or App Store
  - **appName**: application name
  - **userAgent**: the User-Agent request header
  - **country**: country code, compliant with the ISO 3166 standard
  - **city**: city name
  - **zipCode**: postal code
  - **lat**: latitude
  - **lon**: longitude
  - **ipHash**: encrypted user IP address
  - **timestamp**: Epoch time

  In order to change columns' names edit all **\*_daily** constants in `src/constants/constants.py`.

- #### Grouped data

  Files may contain data from various days.

  | **user** | **occured_at** | **latitude** | **longitude** |
  |   :---:    |     :---:     |    :---:    |     :---:     |
  | -615893454 | 2020-03-08 14:57:23.211999 | 52.894363 | 19.835129 |

  - **user**: user identifier
  - **occured_at**: time in "YYYY-MM-DD hh:mm:ss.s" format
  - **latitude**: latitude
  - **longitude**: longitude

  In order to change columns' names edit all **\*_grouped** constants in `src/contants/constants.py`.

### Running preprocessing script

The script for preprocessing can be run with:

```
python3 -m scripts.preprocessing [path] [-d] [-s SINGLE_DAY] [-i] [-v] [-h]
```

To preprocess single daily file, run:

```
python3 -m scripts.preprocessing [path] -s SINGLE_DAY [-i]
```

#### Preprocessing parameters

* `[path]` Path to existing, empty directory, where output files will be generated, (default=`preprocessed`)
* `[-d, --daily]` Run daily preprocessing, (default=False)
* `[-s SINGLE_DAY, --single-day SINGLE_DAY]` Run daily preprocessing for single day, SINGLE_DAY should be passed in YYYYMMDD format
* `[-i, --ignore-single]` Ignore non-moving users in daily preprocessing, (default=False, requires `[-d, --daily]`)
* `[-v, --verbose]` Will display extra runtime info for grouped preprocessing, (default=False, without `[-d, --daily]`)
* `[-h, --help]` Default help option prints help message

After running preprocessing script, there will be a different subdirectory in `path` for every country in dataset (when using *grouped* dataset,
subdirectory for `default_country` from `src/constants/constants.py` is created).

## Grouping

### geoJSON

Default points of interest are provided in `geoJSON` directory. `filtered` subdirectory contains filtered geoJSONs from `original` subdirectory.

To use different set of points, optionally remove existing and add new to `original` subdirectory. To filter geoJSONs, run:

```
python3 -m scripts.poi_filter
```

Filtering script removes points which do not have `name` key and for schools allows only the ones where the name contains any keyword from `schools` array in `src/contants/constants.py`

### Cutoff distances

When deciding whether point should be classified to certain POI type, the script calculates distance to nearest POI of that type and checks if that distance is lower or equal to defined cutoff distance. These distances (expressed in arc degrees) are defined separately for each POI type and are stored in `params/cutoff_distances.json` file. To define your own cutoff distances, simply edit above file.

### Running grouping script

The script for grouping can be run with:

```
python3 -m scripts.poi_grouping [preprocessed_path] [results_path] [country] [-d] [-c] [-s SINGLE_DAY] [-f] [-v] [-h]
```

To run grouping on single daily file, run:

```
python3 -m scripts.poi_grouping [preprocessed_path] [results_path] [country] [-d] [-c] -s SINGLE_DAY [-f] [-v]
```

#### Grouping parameters

* `[preprocessed_path]` Path to preprocessing results directory, (default=`preprocessed`)
* `[results_path]` Path to store grouping results, (default=`results`)
* `[country]` Country to group data from, (default=`default_country`)
* `[-d, --daily]` Run daily grouping (daily dataset), (default=False)
* `[-c, --closest]` Classify points only to closest POI, (default=True)
* `[-s SINGLE_DAY, --single-day SINGLE_DAY]` Run grouping for single day, should be passed in YYYYMMDD format
* `[-f, --filtered]` Run for filtered POI list, (default=True)
* `[-h, --help]` Default help option prints help message

After running grouping script, `results_path` will have the same directories structure as `preprocessed_path` with output .json file for every day.

## Creating visualizations

In order to run visualizations script you will need to have directories generated
with POI grouping in your results folder (one directory for every country).

The script for creating visualizations can be run with:

```
python3 -m scripts.visualize_all [-i] [-b CHANGE_TO_BASE] [-c] [-h]
```

The inputs are taken from `results` folder and visualizations are stored in
 `visualizations` folder.

### Visualizations parameters

* `[-i, --corona_info]` When this option is selected, all graphs will have marked dates related to
major coronavirus related events in Poland. Requires data with dates from March 2020
*  `[-b CHANGE_TO_BASE, --change_to_base CHANGE_TO_BASE]` This parameter is used for setting base date.
All data from dates up to base date are averaged out and used for calculation 
of base value, then all data are shown as change relative to base
`CHANGE_TO_BASE` is taken in `%Y%m%d` format. In order to disable graphs
 with change to base use `-b ""`. Default value is provided, see with `-h`
* `[-c, --clean]` When selected, previous visualizations will be deleted
* `[-h, --help]` Default help option prints help message

### Results description
All results are stored in `visualizations` folder. There is a generated 
subdirectory with visualizations for every subdirectory from `results` folder.

In each subdirectory there are folders for all POI types
(from geoJSON files). There are 3 visualization types provided for every POI type:

* **Classic** - the counts for a POI type in a given day are left unchanged and
displayed,
* **Normalized** - the counts for all POI types in a given day are scaled to
10^6 daily data points (so when for a given day there are 10^6
data points, normal will be the same as normalized),
* **Share of total** - this graph type shows what percentage of data points from
a given day fell into a particular POI type.

Also when `CHANGE_TO_BASE` is set, every visualization type has its "relative to
base counterpart", so a total of 6 types are created.

## Authors

- Jan Bednarski ([@jbednarski](https://github.com/jbednarski))
- Mikołaj Grzywacz ([@Mikolaj6](https://github.com/Mikolaj6))
- Maciej Kozłowski ([@mkozlowski98](https://github.com/mkozlowski98))
- Kacper Rokicki ([@k-rokicki](https://github.com/k-rokicki))
