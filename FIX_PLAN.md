# Fix Plan for Missing Roo CLI

## Problem
The Roo CLI is not found at the expected path `./ai_dev_bot_platform/venv/bin/roo` because the virtual environment doesn't exist.

## Solution
We'll implement a comprehensive fix that:
1. Creates the virtual environment
2. Installs the Roo CLI
3. Updates documentation
4. Adds verification steps

## Steps to Implement

### 1. Create Virtual Environment
```bash
python3 -m venv ./ai_dev_bot_platform/venv
```

### 2. Install Roo CLI
```bash
source ./ai_dev_bot_platform/venv/bin/activate
pip install roo-ai
```

### 3. Verify Installation
```bash
./ai_dev_bot_platform/venv/bin/roo --version
```

### 4. Update README.md
Add installation section:
```markdown
## Installation

1. Create virtual environment:
   ```bash
   python3 -m venv ./ai_dev_bot_platform/venv
   ```
   
2. Activate environment and install dependencies:
   ```bash
   source ./ai_dev_bot_platform/venv/bin/activate
   pip install -r requirements.txt
   pip install roo-ai
   ```
```

### 5. Test the Fix
```bash
python run_autonomy.py
```

## Verification
- Confirm Roo CLI exists at `./ai_dev_bot_platform/venv/bin/roo`
- Check that script runs without errors
- Verify README.md includes installation instructions