#!/bin/bash

# Setup script for FastAPI project
# Creates virtual environment "autoagent" and installs dependencies

set -e  # stop on error

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

VENV_DIR="$PROJECT_DIR/autoagent"
REQ_FILE="$PROJECT_DIR/requirements.txt"

echo "-----------------------------------------"
echo " 🔧 Setting up Python Virtual Environment"
echo "-----------------------------------------"

# Check for Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install Python3 and rerun."
    exit 1
fi

# Remove old venv if needed
if [ -d "$VENV_DIR" ]; then
    echo "⚠️ Virtual environment already exists: $VENV_DIR"
    echo "Recreating it..."
    rm -rf "$VENV_DIR"
fi

# Create virtual environment
echo "✅ Creating virtual environment: autoagent"
python3 -m venv "$VENV_DIR"

# Activate venv
echo "✅ Activating virtual environment"
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "✅ Upgrading pip"
pip install --upgrade pip

# Install dependencies
if [ -f "$REQ_FILE" ]; then
    echo "✅ Installing dependencies from requirements.txt"
    pip install -r "$REQ_FILE"
else
    echo "⚠️ requirements.txt not found. Skipping package installation."
fi

echo "-----------------------------------------"
echo " ✅ Setup complete!"
echo " Virtual environment: $VENV_DIR"
echo " To activate: source autoagent/bin/activate"
echo "-----------------------------------------"

