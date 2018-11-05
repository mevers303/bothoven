#!/usr/bin/env bash

source activate tensorflow_p36
cd bothoven
export PYTHONPATH=src
python src/model.py chopin_2hand_m21 --epochs 15
# sudo shutdown -hP now
