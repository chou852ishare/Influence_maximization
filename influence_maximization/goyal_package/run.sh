#!/bin/bash


m=greedy
n=heplt2
for S in $(seq 10 5 50); do
    nohup ./InfluenceModels -c config_${m}.txt -budget ${S} -outdir ./output/${n}/${n}_${S}_0_${m}/ -probGraphFile ./${n}.inf &
done
