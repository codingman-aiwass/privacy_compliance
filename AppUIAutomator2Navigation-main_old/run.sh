#!/bin/bash
path_to_conda=$(conda info --base)
source $path_to_conda"/etc/profile.d/conda.sh"
conda activate py310
param=$1
python3 run.py $param