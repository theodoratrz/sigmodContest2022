#!/bin/bash

# exit immediately if anything fails
set -e

rm -f ./__pycache__/*

if [ -d __pycache__ ]; then
    rmdir ./__pycache__
fi

rm submission.rpz
rm .reprozip-trace/*
rmdir .reprozip-trace

exit 0
