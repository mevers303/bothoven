#!/usr/bin/env bash

sudo apt update
sudo apt upgrade -y
sudo apt dist-upgrade -y
sudo apt install htop screen

source activate tensorflow_p36
conda upgrade --all -y
pip install --upgrade tensorflow-gpu
pip install tensorboard keras music21
source deactivate

screen -S training bash run.sh
