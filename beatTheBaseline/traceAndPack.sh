#!/bin/bash

# exit immediately if anything fails
set -e

if [ -d __pycache__ ]; then
    # Reprozip complains when __pycache__ files are read & written
    rm __pycache__/*
    rmdir __pycache__
fi

echo "----------------- Running -----------------"
reprozip trace python3 blocking.py
echo "----------------- Packing -----------------"
reprozip pack submission.rpz

exit 0
