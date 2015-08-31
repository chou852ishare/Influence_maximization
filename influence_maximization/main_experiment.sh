#!/bin/bash

for S in $(seq 5 5 50); do
    for T in $(seq 3 2 10); do
        nohup python experiment_lp_mip_benders.py ${S} ${T} epinions benders & # benders lp mip
    done
done
