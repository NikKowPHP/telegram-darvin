#!/bin/bash

# This script will exit immediately if any command fails.
set -e

echo "--- Starting Project Environment Setup ---"

# --- Step 1: Clean up any old, broken virtual environment ---
if [ -d ".venv" ]; then
  echo "⚠️ Found an old .venv directory. Removing it to ensure a clean setup..."
  rm -rf .venv
fi

# --- Step 2: Create a fresh Python virtual environment ---
echo "🐍 Creating a new Python virtual environment in './.venv'..."
python3 -m venv .venv

# --- Step 3: Activate the environment for this script's context ---
# This ensures we use the pip from our new .venv, not the system pip.
echo "🚀 Activating the virtual environment for installation..."
source .venv/bin/activate

# --- Step 4: Install dependencies into the new environment ---
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "--- ✅ Setup Complete! ---"
echo ""
echo "Your environment is ready. Here's what to do next:"
echo ""
echo "1. If you want to use the terminal for commands, run:"
echo "   source .venv/bin/activate"
echo ""
echo "2. **IMPORTANT FOR VS CODE:** To make the Roo extension work correctly,"
echo "   you MUST select the new interpreter:"
echo "   - Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)"
echo "   - Type and select: 'Python: Select Interpreter'"
echo "   - Choose the one that says './.venv/bin/python' (It may be recommended)."
echo ""