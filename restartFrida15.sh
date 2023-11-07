# /bin/bash
# 该脚本在宿主机运行python run_docker.py之后，在进入docker容器后使用
adb devices
frida_server_running=$(adb shell ps -e | grep frida15)

if [[ -n $frida_server_running ]]; then
  echo "frida-server is running. Killing..."
  adb shell su -c killall frida15
  echo "Starting..."
  adb shell su -c ./data/local/tmp/frida15 &
else
  echo "frida-server is not running. Starting..."
  adb shell su -c ./data/local/tmp/frida15 &
fi
exit