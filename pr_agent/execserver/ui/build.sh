#!/bin/bash
# Build script for PR-Agent UI

set -e  # Exit on error

# Display build info
echo "Building PR-Agent UI..."
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building application..."
npm run build

# Ensure dist directory exists
mkdir -p dist

# Copy favicon if it doesn't exist in the output
if [ ! -f dist/favicon.ico ]; then
  echo "Adding favicon.ico..."
  cp -f $(dirname "$0")/src/favicon.ico dist/ 2>/dev/null || echo "No favicon found to copy"
fi

# Create a .gitkeep file in the assets directory to ensure it's tracked by git
mkdir -p dist/assets
touch dist/assets/.gitkeep

echo "Build completed successfully!"
