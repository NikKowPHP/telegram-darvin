#!/bin/bash
# Run test suite and generate audit report

# Exit on any error
set -e

# Activate virtual environment
source .venv/bin/activate

# Run tests
echo "Running test suite..."
pytest --alluredir=allure-results

# Generate audit report
echo "Generating audit report..."
allure generate allure-results -o allure-report --clean

echo "Audit process complete. Report available in allure-report directory."