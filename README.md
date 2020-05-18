# covid-pegasus

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
* [Authors](#authors)

## Getting started

### Prerequisites

To run covid-pegasus, you will need the newest version of Anaconda, available via the following link:

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

This will create new environment named "covid-pegasus". To activate it, run:

```
conda activate covid-pegasus
```

All of the following instructions need to be executed with covid-pegasus environment activated.

To deactivate environment, just run:

```
conda deactivate
```

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

  | **user** | **latitude** | **longitude** | **occured_at** |
  |   :---:    |     :---:     |    :---:    |     :---:     |
  | -615893454 | 52.894363 | 19.835129 | 2020-03-08 14:57:23.211999 |

  - **user**: user identifier
  - **latitude**: latitude
  - **longitude**: longitude
  - **occured_at**: time in "YYYY-MM-DD hh:mm:ss.s" format

  In order to change columns' names edit all **\*_grouped** constants in `src/contants/constants.py`.

### Running preprocessing script

The script for preprocessing can be run with:

```
python3 -m scripts.preprocessing [path] [-d, --daily] [-s SINGLE_DAY, --single-day SINGLE_DAY] [-i, --ignore-single] [-v, --verbose] [-h, --help]
```

To preprocess single daily file, run:

```
python3 -m scripts.preprocessing -s YYYYMMDD [-i] [path]
```

#### Preprocessing parameters

* `[path]` Path to existing, empty directory, where output files will be generated, (default=`preprocessed`).
* `[-d, --daily]` Run daily preprocessing, (default=False).
* `[-s SINGLE_DAY, --single-day SINGLE_DAY]` Run daily preprocessing for single day, SINGLE_DAY should be passed in YYYYMMDD format. 
* `[-i, --ignore-single]` Ignore non-moving users in daily preprocessing, (default=False, requires `[-d, --daily]`).
* `[-v, --verbose]` Will display extra runtime info for grouped preprocessing, (default=False, without `[-d, --daily]`).
* `[-h, --help]` Default help option prints help message.

## Authors

- Jan Bednarski ([@jbednarski](https://github.com/jbednarski))
- Mikołaj Grzywacz ([@Mikolaj6](https://github.com/Mikolaj6))
- Maciej Kozłowski ([@mkozlowski98](https://github.com/mkozlowski98))
- Kacper Rokicki ([@k-rokicki](https://github.com/k-rokicki))
