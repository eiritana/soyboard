#!/bin/sh
set -e
docker stop "$(docker ps -a -q  --filter ancestor=soyboard)"
docker-compose build
docker cp "$(docker ps -a -q  --filter ancestor=soyboard)":/app/soyboard/test.db .
docker-compose run -d --rm -p 0.0.0.0:80:80 soyboard
docker cp test.db "$(docker ps -a -q  --filter ancestor=soyboard)":/app/soyboard/
