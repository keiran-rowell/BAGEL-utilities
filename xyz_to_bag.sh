#! /usr/bin/bash

filename=$1
base=${filename%.xyz}
echo $base

while read line
do
    awk 'NR>1 {print "{ \"atom\" : \"" $1 "\", \"xyz\" : ["  $2", " $3", " $4"] }," }' > $base.bag
done < $1

sed -i '$ s/.$//' $base.bag
