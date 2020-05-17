#!/bin/bash

echo "Running init."

dir_path="$(dirname "$(readlink -f "$0")")"

cd "$dir_path/.." &&
mkdir data preprocessed results &&
echo "Success, created all folders" ||
echo "Failed creating folders"
