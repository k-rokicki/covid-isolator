# covid-pegasus

Tool for monitoring of human aggregates during quarantine using geolocation data

## Table of Contents


* [Getting started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Creating an environment](#creating-an-environment)
* [Creating visualizations](#creating-visualizations)
  * [Visualize params](#visualize-params)
  * [Results description](#results-description)
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

## Creating visualizations

In order to run visualizations scripts you will need to have directories generated
 with poi-groping in your results folder (one directory per poi-grouping configuration).

The script for creating visualizations can be run with:

```
python3 -m scripts.visualize_all [-h] [-i] [-b CHANGE_TO_BASE] [-c]
```

The inputs are taken from `results` folder and visualizations are stored in
 `visualizations` folder.

### Visualize params
* `[-h]` Default help option prints help message.

* `[-i]` When this option is selected all graphs will have marked dates related to 
major coronavirus related events in Poland. Requires data with dates from march 2020.
 
*  `[-b CHANGE_TO_BASE]` This parameter is used for setting base date. 
All data from dates up to base date are averaged out and used for calculation 
of base value, then all data are shown as change relative to base. 
`CHANGE_TO_BASE` is taken in `%Y%m%d` format. In order to disable graphs
 with change to base use `-b ""`. Default value is provided, see with `-h`.

* `[-c]` When selected previous visualizations will be cleaned.

### Results description
All results are stored in `visualizations` folder. There is a generated 
directory with visualizations for every configuration from `results` folder.

In each configuration folder there are directories for all POI types 
(from geojsons). There are 3 visualization types provided for every POI:

* **Normal** - The counts for a POI type in a given day are left unchanged and 
displayed.

* **Normalized** - The counts for all POI types in a given day are scaled. They are 
scaled to 10^6 daily data points (so when for a given day there are 10^6 
data points, normal will be the same as normalized). 

* **Share of total** - This graph type shows what percentage of data points from 
a given day fell into a particular POI type.

Also when change to base is set, every visualization type has its "relative to 
base counterpart", so a total of 6 types.

## Authors

- Jan Bednarski ([@jbednarski](https://github.com/jbednarski))
- Mikołaj Grzywacz ([@Mikolaj6](https://github.com/Mikolaj6))
- Maciej Kozłowski ([@mkozlowski98](https://github.com/mkozlowski98))
- Kacper Rokicki ([@k-rokicki](https://github.com/k-rokicki))
