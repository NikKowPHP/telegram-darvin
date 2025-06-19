#!/bin/bash
cd ai_dev_bot_platform
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
pytest --disable-warnings