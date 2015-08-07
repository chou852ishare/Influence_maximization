#!/bin/bash

for S in $(seq 5 5 50); do
    for T in $(seq 3 2 10); do
        nohup python experiment_lp_mip_benders.py ${S} ${T} heplt2 benders & # lp mip
        if [ ${S} == 5 ] && [ ${T} == 1 ]; then
            echo "sleep 5m"
            sleep 5m
        fi
    done
done
