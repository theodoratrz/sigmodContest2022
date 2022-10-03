#!/bin/bash

# exit immediately if anything fails
set -e

# Reprozip complains when __pycache__ files are read & written
rm -f ./__pycache__/*

if [ -d __pycache__ ]; then
    rmdir ./__pycache__
fi

echo "----------------- Running -----------------"
reprozip trace python3 run.py
echo "----------------- Packing -----------------"
reprozip pack submission.rpz

exit 0
