#!/bin/bash

# run this script to set up the machine

sudo mkdir -p /data/jupyterhub/users
sudo mkdir -p /data/jupyterhub/shared_datasets
# Set the correct permissions so Docker can write to them (ID 1000 is the jovyan user)
sudo chown -R 1000:1000 /data/jupyterhub

jq -r '.[]' images.json | while IFS= read -r image; do
    docker pull "$image"
done

docker compose up -d
