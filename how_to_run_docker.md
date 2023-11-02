### Prerequisites
1. Python3
2. Docker
3. adb tool
4. A real phone with frida-server version 15.1.24 plugged in your machine, and they are in the same Wi-Fi network. And you should use delete ~/.android folder and execute command `adb devices` in your local machine and make the phone trust your machine first. You can do this with the following steps: 1. run `rm -rf ~/.android` 2. run `adb devces` and press allowing debug with this machine all the time.

### Setup && RUN
1. Find the config.ini file in ./privacy_compliance, and change the value of run_in_docker to 'true'.
2. Run `powershell.exe .\build_image.ps1` in Windows, or run `sh build_image.sh` in Unix-Like OS.
3. Run `python run_docker.py` in Windows, or run `sudo python3 run_docker.py` in Unix-Like OS.
4. Now you are in the docker container. Run `conda deactivate`
5. Now you can run the python script to start analysis. Run `sudo python3 run.py -c config.ini`

### Analysis Results
Results are stored in ./docker_result. You can modify the running settings in the confg.ini file in ./docker_result.