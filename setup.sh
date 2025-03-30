#!/bin/bash
# MaliSafi Real Estate Agent - Setup Script

echo "Setting up MaliSafi Real Estate Agent..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
SECRET_KEY=malisafi-development-key
OPENAI_API_KEY=your_openai_api_key_here
EOL
    echo "Please update the .env file with your OpenAI API key"
fi

# Make run scripts executable
chmod +x run_dev.sh
chmod +x deploy_prod.sh

echo "Setup complete! To run the application:"
echo "1. Update the .env file with your OpenAI API key"
echo "2. Run 'python3 app.py'"
echo "3. Open http://localhost:5000 in your browser"
