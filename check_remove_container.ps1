$containerName = "privacy_compliance"

# 检查容器是否存在
$containerExists = (docker ps -a --format '{{.Names}}' | Select-String -Pattern "^$containerName$")

if ($containerExists) {
    Write-Host "Container '$containerName' exists. Removing..."
    docker rm -f $containerName
    Write-Host "'$containerName' removed..."
} else {
    Write-Host "Container '$containerName' does not exist."
}