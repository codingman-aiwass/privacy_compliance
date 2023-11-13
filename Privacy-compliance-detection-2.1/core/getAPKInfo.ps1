chcp 65001
$env:JAVA_TOOL_OPTIONS = "-Dfile.encoding=UTF-8"

Write-Host "Start get APK Info!"
java -jar getApkInfo.jar