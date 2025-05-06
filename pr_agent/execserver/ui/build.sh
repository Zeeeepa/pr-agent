#!/bin/bash

# Build script for the PR-Agent UI

echo "Building PR-Agent UI..."

# Install dependencies
npm install

# Build the application
npm run build

# Copy the build files to the static directory
rm -rf static/js static/css static/assets
mkdir -p static/js static/css static/assets
cp -r dist/* static/

echo "Build complete! UI files have been copied to the static directory."

