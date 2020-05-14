# covid-pegasus

Tool for monitoring of human aggregates during quarantine using geolocation data

## Table of Contents


* [Getting started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Creating an environment](#creating-an-environment)
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

## Authors

- Jan Bednarski ([@jbednarski](https://github.com/jbednarski))
- Mikołaj Grzywacz ([@Mikolaj6](https://github.com/Mikolaj6))
- Maciej Kozłowski ([@mkozlowski98](https://github.com/mkozlowski98))
- Kacper Rokicki ([@k-rokicki](https://github.com/k-rokicki))
