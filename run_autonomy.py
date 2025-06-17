#!/usr/bin/env python3
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_orchestrator():
    """Execute the Orchestrator agent using the Roo CLI"""
    try:
        result = subprocess.run(
            ['./ai_dev_bot极_platform/venv/bin/python', '-m', 'src.code_context_tool.cli', 'orchestrator'],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Orchestrator executed successfully:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Orchestrator execution failed:\n{e.stderr}")

def main():
    """Main execution loop"""
    logger.info("Starting autonomous development loop")
    while True:
        try:
            run_orchestrator()
            # Pause for 10 seconds between executions
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Autonomous loop interrupted by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(30)  # Longer pause after errors

if __name__ == "__main__":
    main()