#!/bin/sh
# FIXME: this will be deleted soon because Docker isn't
# setup right yet for this repo.
docker cp soyboard/test.db /tmp
docker stop "$(docker ps -a -q  --filter ancestor=soyboard)"
docker-compose build
docker-compose run -d --rm -p 0.0.0.0:80:80 soyboard
docker cp /tmp/test.db soyboard/test.db
