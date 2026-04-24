#!/bin/bash

# run this script to set up the machine

sudo mkdir -p /data/jupyterhub/users
sudo mkdir -p /data/jupyterhub/shared_datasets
# Set the correct permissions so Docker can write to them (ID 1000 is the jovyan user)
sudo chown -R 1000:1000 /data/jupyterhub

jq -r '.[]' images.json | while IFS= read -r image; do
    docker pull "$image"
done

# get the current machine's IP address to pass to the homepage container
THINKSTATION_IP=$(hostname -I | awk '{print $1}')

# create a .env file with the THINKSTATION_IP variable for docker-compose to use
echo "THINKSTATION_IP=${THINKSTATION_IP}" > .env

docker compose up -d
