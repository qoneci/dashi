#!/bin/bash

docker build -t 'dashi:nginx' --rm=true --no-cache=true -f Dockerfile-nginx .
docker build -t 'dashi:web' --rm=true --no-cache=true -f Dockerfile-web .
