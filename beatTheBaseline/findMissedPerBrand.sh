#!/bin/bash

#read -r columnHeaders < missed.csv
for brand in "sony" "toshiba" "kingston" "sandisk" "intenso" "lexar" "transcend" "samsung" "pny"; do
    #printf "$columnHeaders\n" > "./missed/missed_$brand.csv"
    #cat missed.csv | grep -i $brand >> "./missed/missed_$brand.csv"
    cat missed.csv | grep -i $brand > "./missed/missed_$brand.csv"
    lines=$(wc -l < "./missed/missed_$brand.csv")
    printf "$brand: $lines\n"
done | column -t
exit 0
