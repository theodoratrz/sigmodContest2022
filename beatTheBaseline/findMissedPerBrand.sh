#!/bin/bash
for brand in "sony" "toshiba" "kingston" "sandisk" "intenso" "lexar" "transcend" "samsung" "pny"; do
    cat missed.csv | grep -i $brand > "./missed/missed_$brand.csv"
    lines=$(wc -l < "./missed/missed_$brand.csv")
    printf "$brand: $lines\n"
done | column -t
exit 0
