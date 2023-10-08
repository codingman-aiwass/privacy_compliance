#!/bin/bash

# 检查容器是否存在
container_exists=$(docker ps -a --format '{{.Names}}' | grep -w "test_docker")

if [[ -n $container_exists ]]; then
  echo "Container 'test_docker' exists. Removing..."
  docker rm -f test_docker
else
  echo "Container 'test_docker' does not exist."
fi