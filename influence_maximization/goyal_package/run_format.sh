#!/bin/bash

m=simpath
n=hep_LT2
for S in $(seq 5 5 50); do
     cp ./output/${m}/${n}_${S}/ ~/influence_maximization/output/${n}/${n}_${S}_${m}.seedset
done
