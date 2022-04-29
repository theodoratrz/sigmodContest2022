#!/bin/bash
for brand in "lenovo" "hp" "acer" "sony" "toshiba" "asus" "panasonic" "samsung" "dell"; do
    cat common.csv | grep -i $brand > "./common/common_$brand.csv"
    lines=$(wc -l < "./common/common_$brand.csv")
    printf "$brand: $lines\n"
done | column -t
exit 0
