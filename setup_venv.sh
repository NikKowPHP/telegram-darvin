#!/bin/bash
# Setup virtual environment and install dependencies

# Exit on any error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify pytest installation
echo "Verifying pytest installation..."
pip install pytest

echo "Test environment setup complete."