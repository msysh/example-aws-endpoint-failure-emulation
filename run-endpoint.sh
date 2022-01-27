#!/bin/bash

docker run \
  -it \
  --rm \
  --name ddb-endpoint \
  -p 8080:80 \
  -v ${PWD}/endpoint/400.json:/usr/share/nginx/html/400.json \
  -v ${PWD}/endpoint/500.json:/usr/share/nginx/html/500.json \
  -v ${PWD}/endpoint/nginx.conf:/etc/nginx/nginx.conf \
  nginx:latest