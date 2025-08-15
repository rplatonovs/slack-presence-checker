#!/bin/bash

# Exit immediately if a command fails
set -e

# Absolute path to your project directory
PROJECT_DIR="/root/scripts"

# Move to project directory
cd "$PROJECT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "myenv" ]; then
    python3 -m venv myenv
fi

# Activate virtual environment
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Python script with provided arguments
python3 check_presence.py \
	sample1@email.com \
    sample2@email.com \

# Deactivate environment
deactivate
