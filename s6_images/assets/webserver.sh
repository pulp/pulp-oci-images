#!/bin/bash

if [ "${SCHEME}" = "https" ]; then
  cp -avr /nginx/ssl_nginx.conf /etc/nginx/nginx.conf
else
  cp -avr /nginx/nginx.conf /etc/nginx/nginx.conf
fi
