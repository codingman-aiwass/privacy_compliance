if (-not (Test-Path "$PWD/logsPath")) {
    New-Item -ItemType Directory -Path "$PWD/logsPath"
}

if (-not (Test-Path "$PWD/ResultSaveDir")) {
    New-Item -ItemType Directory -Path "$PWD/ResultSaveDir"
}

if (-not (Test-Path "$PWD/PrivacyPolicySaveDir")) {
    New-Item -ItemType Directory -Path "$PWD/PrivacyPolicySaveDir"
}

if (-not (Test-Path "$PWD/final_res/pp_missing")) {
    New-Item -ItemType Directory -Path "$PWD/final_res/pp_missing" -Force
}

Write-Host "Start static analysis..."
java -jar find_data_points.jar