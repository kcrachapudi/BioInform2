#!/bin/bash

echo "🧹 Cleaning BioInform2 project..."

# Create folders if missing
mkdir -p results logs work

# Remove generated files
rm -f results/*
rm -f logs/*
rm -rf work/*

echo "✅ Cleanup complete!"