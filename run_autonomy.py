import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(test_mode=False):
    logger.info("Starting autonomous development loop")
    while True:
        try:
            # Execute the Orchestrator agent
            result = subprocess.run(
                ['roo', '-m', 'orchestrator'],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Orchestrator executed successfully:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Orchestrator execution failed with exit code {e.returncode}:\n{e.stderr}")
        except FileNotFoundError as e:
            logger.error(f"Command not found: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        # Sleep before next iteration or break
        sleep_time = 30  # Longer pause after errors
        if test_mode:
            break
        logger.info(f"Sleeping for {sleep_time} seconds before next iteration")
        time.sleep(sleep_time)

if __name__ == '__main__':
    main()