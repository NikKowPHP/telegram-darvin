#!/bin/bash
# Create virtual environment
python3 -m venv ai_dev_bot_platform/venv --clear
# Activate virtual environment
source ai_dev_bot_platform/venv/bin/activate
# Install requirements
pip install -r ai_dev_bot_platform/requirements.txt --quiet