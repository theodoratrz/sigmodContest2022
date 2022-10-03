#!/bin/bash

for brand in "lenovo" "hp" "acer" "sony" "toshiba" "asus" "panasonic" "samsung" "dell"; do
    cat ../output_misc/common.csv | grep -i $brand > "../output_misc/common/common_$brand.csv"
    lines=$(wc -l < "../output_misc/common/common_$brand.csv")
    printf "$brand: $lines\n"
done | column -t
exit 0
