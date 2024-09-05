#!/bin/bash

# update & install system dependencies
sudo apt-get update
sudo apt-get install -y python3-venv ffmpeg

# Create and enable virtual env
python3 -m venv myenv
source myenv/bin/activate

# Install python dependencies
pip install -r requirements.txt

echo "Setup complete. Virtual environment created and dependencies installed."
