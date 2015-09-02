#!/bin/bash

n=epinions
m=maxweight
for S in $(seq 25 5 50); do
    for T in $(seq 1 2 5); do
        python experiment_lp_mip_benders.py ${S} ${T} ${n} ${m}
    done
done
