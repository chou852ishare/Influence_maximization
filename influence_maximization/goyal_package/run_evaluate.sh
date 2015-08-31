#!/bin/bash

n=heplt2
m=maxlp
for S in $(seq 15 5 50); do
    for T in $(seq 1 2 9); do
        ./InfluenceModels -c config_evaluate.txt -budget ${S} -seedFileName ../output/${n}/${n}_${S}_${T}_${m}.seedset #-outdir ./output/${n}/${n}_${S}_${T}_${m}
    done
done
