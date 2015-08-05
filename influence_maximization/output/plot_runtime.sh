#!/bin/bash

data=$1

gnuplot<<EOF -persist
set term x11
plot "${data}" with linespoints
EOF
