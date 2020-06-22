#!/bin/bash

file=$1
out_file_name=$2

num_atoms=$(grep -A 1 "\[GEOMETRIES\] (XYZ)" $file | tail -1)

geom_context=$((num_atoms+3))

grep -B $geom_context "point   0" $file | head -n -2 > $out_file_name
