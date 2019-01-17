#!/usr/bin/env bash

sudo apt update
sudo apt dist-upgrade -y
sudo apt install screen -y

source activate tensorflow_p36
conda upgrade --all -y
pip install tensorflow tensorboard keras music21 boto3
