#!/bin/bash
for brand in "sony" "toshiba" "kingston" "sandisk" "intenso" "lexar" "transcend" "samsung" "pny"; do
    cat false.csv | grep -i $brand > "./false/false_$brand.csv"
    lines=$(wc -l < "./false/false_$brand.csv")
    printf "$brand: $lines\n"
done | column -t
exit 0
