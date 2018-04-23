#!/bin/sh
# FIXME: this is a temporary script until I ustart storing
# test.db outside the docker container or until I setup postgres service...
set -e
docker cp "$(docker ps -a -q  --filter ancestor=soyboard)":/app/soyboard/test.db .
docker stop "$(docker ps -a -q  --filter ancestor=soyboard)"
docker-compose build
docker-compose run -d --rm -p 0.0.0.0:80:80 soyboard
docker cp test.db "$(docker ps -a -q  --filter ancestor=soyboard)":/app/soyboard/
