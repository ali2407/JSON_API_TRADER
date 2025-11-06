#!/bin/bash

# Setup script for JSON API Trader

echo "==================================="
echo "JSON API Trader Setup"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your BingX API credentials"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create necessary directories
mkdir -p trades
mkdir -p logs

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your BingX API credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the terminal: python main.py"
echo ""
echo "For testing, keep TESTNET=true in .env"
echo ""
