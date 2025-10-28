#!/bin/bash
# Development environment setup for mikro-manager

set -e

echo "Setting up mikro-manager development environment..."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install paramiko pyyaml librouteros

# Install packages in development mode
echo "Installing mikro-common in development mode..."
cd mikro-common
pip install -e .
cd ..

echo "Installing mikro-dns in development mode..."
cd mikro-dns
pip install -e .
cd ..

echo "Installing mikro-api-utils in development mode..."
cd mikro-api-utils
pip install -e .
cd ..

echo ""
echo "✓ Development environment ready!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To test:"
echo "  export MIKRO_CONFIG_DIR=~/Development/GitHub/mikro-manager/test-config"
echo "  mikro-dns list"
echo "  mikro-api-utils test"
echo ""
