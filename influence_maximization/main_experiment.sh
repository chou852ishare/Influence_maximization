#!/bin/bash

for S in $(seq 5 5 50); do
    for T in $(seq 1 2 10); do
        nohup python experiment_lpIM_nobigM.py ${S} ${T} heplt2 mip & # lp
    done
done
