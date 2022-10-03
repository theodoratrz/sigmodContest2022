#!/bin/bash

for brand in "sony" "toshiba" "kingston" "sandisk" "intenso" "lexar" "transcend" "samsung" "pny"; do
    cat ../output_misc/missed.csv | grep -i $brand > "../output_misc/missed/missed_$brand.csv"
    lines=$(wc -l < "../output_misc/missed/missed_$brand.csv")
    printf "$brand: $lines\n"
done | column -t
exit 0
