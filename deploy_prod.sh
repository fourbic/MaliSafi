#!/bin/bash

# MaliSafi Real Estate Agent - Production Deployment Script
echo "Deploying MaliSafi Real Estate Agent in production mode..."

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install or update dependencies including gunicorn
echo "Installing dependencies..."
pip install -r requirements.txt
pip install gunicorn

# Set environment to production
export FLASK_ENV=production
export FLASK_DEBUG=0

# Run the application with gunicorn
echo "Starting production server with Gunicorn..."
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "app:app" 