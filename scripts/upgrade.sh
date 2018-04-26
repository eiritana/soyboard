#!/bin/sh
# FIXME: this will be deleted soon because Docker isn't
# setup right yet for this repo.

set -e

echo "Backup database to /tmp..."
cp soyboard/test.db /tmp

echo "Build new Docker image!"
docker-compose build

echo "Stop any currently running soyboard containers..."
docker stop "$(docker ps -a -q  --filter ancestor=soyboard)"

echo "Run new image and serve!"
docker-compose run --env-file ./.env-file -d --rm -p 0.0.0.0:80:80 soyboard

echo "Copy database from backup to Docker location!"
cp /tmp/test.db soyboard/test.db
