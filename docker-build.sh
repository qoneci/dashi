#!/bin/bash

docker build -t 'dashi:web' --rm=true --no-cache=true -f Dockerfile .
