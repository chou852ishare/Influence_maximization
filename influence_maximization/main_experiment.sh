#!/bin/bash

n=pwh
m=mip
for S in $(seq 5 5 25); do
    for T in $(seq 1 2 3); do
        python experiment_lp_mip_benders.py ${S} ${T} ${n} ${m}
    done
done
