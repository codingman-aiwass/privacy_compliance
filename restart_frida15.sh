# /bin/bash
adb devices
adb shell su -c setenforce 0
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