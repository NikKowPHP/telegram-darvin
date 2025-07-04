@echo off
REM Setup virtual environment and install dependencies for Windows

REM Create virtual environment if it doesn't exist
if not exist "ai_dev_bot_platform\venv" (
  echo Creating virtual environment...
  py -m venv ai_dev_bot_platform\venv
)

REM Activate virtual environment
call ai_dev_bot_platform\venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r ai_dev_bot_platform\requirements.txt

REM Verify pytest installation
echo Verifying pytest installation...
pip install pytest

echo Test environment setup complete.