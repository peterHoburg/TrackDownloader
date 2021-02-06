#!/usr/bin/env bash
docker_container_name="track_downloader:local"

docker build --build-arg DEV=true -t $docker_container_name .
docker run \
  -e ENVIRONMENT="prod" \
  -e USER=$USER \
  -e USERID=$UID \
  -v /$PWD:/opt \
  -it $docker_container_name /bin/bash
