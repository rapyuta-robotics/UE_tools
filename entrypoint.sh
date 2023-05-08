#!/bin/bash

echo "Set User ID: ${USER_ID:-1000}"
usermod -u ${USER_ID:-1000} admin

echo "Set Group ID: ${GROUP_ID:-1000}"
sudo groupmod -g ${GROUP_ID:-1000} admin

exec "$@"