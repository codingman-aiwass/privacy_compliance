#!/bin/bash
current_time=$(date +'%Y-%m-%d:%H:%M:%S')
# python3 run.py -c config.ini > ./logs/total_output_${current_time}.log 2>&1 &
python3 run.py -c config.ini 2>&1 | tee -a ./logs/total_output_${current_time}.log &