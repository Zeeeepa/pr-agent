#!/bin/bash

# Build script for PR-Agent UI

echo "Building PR-Agent UI..."

# Create static directory if it doesn't exist
mkdir -p static

# Install dependencies
npm install

# Build the application
npm run build

# Copy the build output to the static directory
cp -r dist/* static/

echo "Build complete!"
