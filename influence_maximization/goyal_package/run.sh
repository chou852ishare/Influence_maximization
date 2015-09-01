#!/bin/bash

m=simpath # ldag simpath
n=epinions
for S in $(seq 5 5 50); do
    nohup ./InfluenceModels -c config_${m}.txt -budget ${S} -outdir ./output/${n}/${n}_${S}_0_${m}/ -probGraphFile ./graph/${n}.inf &
done
