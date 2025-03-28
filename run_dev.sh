#!/bin/bash

# MaliSafi Real Estate Agent - Development Server Script
echo "Starting MaliSafi Real Estate Agent in development mode..."

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
pip install flask markdown2 python-dotenv requests openai crewai langchain_community crewai '[tools]'
pip install -r requirements.txt

# Run the application in development mode
echo "Starting development server..."
python app.py

# Deactivate virtual environment on exit
deactivate 