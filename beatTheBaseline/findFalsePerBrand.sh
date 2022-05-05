#!/bin/bash

#read -r columnHeaders < false.csv
for brand in "sony" "toshiba" "kingston" "sandisk" "intenso" "lexar" "transcend" "samsung" "pny"; do
    #printf "$columnHeaders\n" > "./false/false_$brand.csv"
    #cat false.csv | grep -i $brand >> "./false/false_$brand.csv"
    cat false.csv | grep -i $brand > "./false/false_$brand.csv"
    lines=$(wc -l < "./false/false_$brand.csv")
    printf "$brand: $lines\n"
done | column -t
exit 0
