#!/bin/bash

# Install system dependencies
sudo apt update
sudo apt install -y libxcb-xinerama0 libxcb-cursor0 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip3 install -r requirements.txt


echo "✅ Setup complete. Virtual environment created, dependencies installed."
