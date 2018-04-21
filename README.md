# soyboard

[![Build
Status](https://travis-ci.org/lily-mayfield/soyboard.svg?branch=master)](https://travis-ci.org/lily-mayfield/soyboard)

One-board imageboard.

This project is in alpha, it is poorly documented and very messy, it is not
recommended for production.

## Production

`docker-compose build; docker run soyboard`

## Testing

### Host

  1. Create and activate a virtual environment
  1. `pip install -r requirements.txt`
  1. In Ubuntu I needed to `sudo apt install libssl-dev`
  1. `python3 -m soyboard`

### Run tests in Docker

`docker-compose build; docker run soyboard pytest`

### Debugging in Docker

`docker-compose build; docker run soyboard debug`
