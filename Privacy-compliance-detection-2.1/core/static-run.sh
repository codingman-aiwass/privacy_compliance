#!/bin/bash

if [ ! -d "$(pwd)/logsPath" ]; then
    mkdir $(pwd)/logsPath
fi

if [ ! -d "$(pwd)/ResultSaveDir" ]; then
    mkdir $(pwd)/ResultSaveDir
fi

if [ ! -d "$(pwd)/PrivacyPolicySaveDir" ]; then
    mkdir $(pwd)/PrivacyPolicySaveDir
fi

if [ ! -d "$(pwd)/final_res/pp_missing" ]; then
    mkdir -p $(pwd)/final_res/pp_missing
fi

echo "Start static analysis..."
java -jar find_data_points.jar

