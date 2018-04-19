#!/bin/bash

chown -R nginx:nginx ${APP_DIR} \
    && chmod 777 ${APP_DIR} -R \
    && chmod 777 /run/ -R \
    && chmod 777 /root/ -R

if [ "$1" == "debug" ]; then 
    echo "Running app in debug mode!"
    python3 app.py
else
    echo "Running app in production mode!"
    nginx && uwsgi --ini /app.ini
fi
