#!/bin/bash
# Run test suite and generate audit report

# Exit on any error
set -e

# Function to check if .venv exists and create it if not
check_venv() {
    if [ ! -d ".venv" ]; then
        echo ".venv not found. Setting up virtual environment..."
        bash setup_venv.sh
        if [ $? -ne 0 ]; then
            echo "Error: Failed to set up virtual environment. Exiting."
            exit 1
        fi
    fi
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed. Please install Python and try again."
    exit 1
fi

# Check if virtual environment exists and create if needed
check_venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation
if ! command -v python &> /dev/null; then
    echo "Error: Failed to activate virtual environment. Exiting."
    exit 1
fi

# Install missing dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies. Exiting."
        exit 1
    fi
fi

# Run tests
echo "Running test suite..."
pytest --alluredir=allure-results

# Generate audit report
echo "Generating audit report..."
allure generate allure-results -o allure-report --clean

echo "Audit process complete. Report available in allure-report directory."