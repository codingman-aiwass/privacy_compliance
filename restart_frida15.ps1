# 运行 adb devices
# TODO 还有bug，等待修复。。。
adb devices

# 检查 frida-server 是否正在运行
$frida_server_running = adb shell ps -e | Select-String -Pattern "frida15" -SimpleMatch -Quiet

if (-not $frida_server_running) {
  $frida_server_running = adb shell ps -e | Select-String -Pattern "frida" -SimpleMatch -Quiet
}

if ($frida_server_running) {
  Write-Host "frida-server is running. Killing..."
  adb shell su -c killall frida15
  Write-Host "Starting..."
  adb shell su -c "/data/local/tmp/frida15"
} else {
  Write-Host "frida-server is not running. Starting..."
  $frida_executable = adb shell ls /data/local/tmp | Select-String -Pattern "frida" -SimpleMatch -Quiet

  if ($frida_executable) {
    adb shell su -c "./data/local/tmp/$($frida_executable)"
  } else {
    Write-Host "No frida executable found in /data/local/tmp directory."
  }
}
Exit