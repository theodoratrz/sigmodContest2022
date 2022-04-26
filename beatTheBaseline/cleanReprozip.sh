#!/bin/bash

# exit immediately if anything fails
set -e

rm submission.rpz
rm .reprozip-trace/*
rmdir .reprozip-trace

if [ -d __pycache__ ]; then
    rm ./__pycache__/*
    rmdir __pycache__
fi

exit 0
