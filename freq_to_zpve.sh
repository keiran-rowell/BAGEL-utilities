#! /bin/bash

CMtoEh=0.0000045563
EhtokJ=2625.50
CMtokJ=0.011963

file=$1

#For every freq line, sum all values
#Excludes negative number by 'if $i does not contain a match for starting with -'
freqsum=$(awk '$1 ~/Freq/ {sum=0} { for (i=1; i<=NF; i++) if ($i !~ /^-/) sum+=$i} END {print sum}' $file)

#ZPVE can be approximated as '1/2 Sum vi'
CM_zpve=$(echo 'scale=2;'$freqsum/2 | bc)
#echo $CM_zpve

#Convert units
kJ_zpve=$(echo 'scale=2;'$CM_zpve*$CMtokJ | bc)
echo $kJ_zpve
