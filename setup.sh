#!/bin/bash
# MaliSafi Real Estate Agent - Setup Script

echo "Setting up MaliSafi Real Estate Agent..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make run scripts executable
chmod +x run_dev.sh
chmod +x deploy_prod.sh

echo "Setup complete! You can now run the application with:"
echo "  ./run_dev.sh    - For development"
echo "  ./deploy_prod.sh - For production"
