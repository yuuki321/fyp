#!/bin/bash

echo "========================================"
echo "   AI Music Generator Installer"
echo "========================================"

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Please install Python 3.8 or higher first."
    exit 1
fi

# Check if FluidSynth is installed
which fluidsynth
if [ $? -ne 0 ]; then
    echo "Warning: FluidSynth not detected. To install FluidSynth:"
    echo "  - On Ubuntu/Debian: sudo apt-get install fluidsynth"
    echo "  - On macOS: brew install fluidsynth"
    echo "  - On CentOS/RHEL: sudo yum install fluidsynth"
    read -p "Continue installation anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo "Creating environment configuration file..."
    cp .env.example .env
    # Generate a random secret key
    RANDOM_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
    # Replace the example key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here/$RANDOM_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here/$RANDOM_KEY/" .env
    fi
fi

# Initialize database
echo "Initializing database..."
flask db upgrade

echo "========================================"
echo "Installation complete!"
echo "To start the application, run:"
echo "source venv/bin/activate"
echo "python run.py"
echo "========================================"