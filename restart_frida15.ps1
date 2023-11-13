# 运行 adb devices
adb devices
adb shell su -c setenforce 0
# 检查 frida-server 是否正在运行
$frida_server_running = adb shell ps -e | Select-String "frida15"

if ($frida_server_running) {
  Write-Host "frida-server is running. Killing..."
  adb shell su -c killall frida15
  Write-Host "Starting..."
  adb shell su -c "./data/local/tmp/frida15"
} else {
  Write-Host "frida-server is not running. Starting..."
  adb shell su -c "./data/local/tmp/frida15"
}
Exit