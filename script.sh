#!/bin/bash

echo "Start Deploy"
cd ~/contain-mini
git pull origin main
cd dev
rm -rf dist/*
sudo ./docker-up.sh docker-compose.yml >> backend.log 2>&1 &
echo "Deploy finish"
