import subprocess
import time
import logging
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_project_manifest():
    """Create the project manifest file with basic structure."""
    manifest_path = 'project_manifest.json'
    manifest_content = {
        "project_root": ".",
        "paths": {
            "log_file": "logs/system_events.log",
            "cct_config": ".cct_config.json",
            "work_items_dir": "work_items/",
            "active_plan_file": "todos/dev_todo_phase_1.md",
            "signal_files": {
                "needs_assistance": "NEEDS_ASSISTANCE.md",
                "needs_refactor": "NEEDS_REFACTOR.md",
                "commit_complete": "COMMIT_COMPLETE.md",
                "tech_lead_approved": "TECH_LEAD_APPROVED.md",
                "qa_approved": "QA_APPROVED.md"
            }
        }
    }

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create system_events.log file
    with open("logs/system_events.log", "w") as log_file:
        log_file.write("System event logging initialized\n")

    # Write manifest file
    with open(manifest_path, "w") as f:
        json.dump(manifest_content, f, indent=4)

    logger.info(f"Created project manifest at {manifest_path}")

def main(test_mode=False):
    logger.info("Starting autonomous development loop")

    # Check if project manifest exists, if not create it
    if not os.path.exists('project_manifest.json'):
        logger.info("Project manifest not found. Initializing blueprint mode...")
        create_project_manifest()

        # Handoff to Architect for blueprint mode
        try:
            result = subprocess.run(
                ['roo', '-m', 'architect', '--command', 'create_blueprint'],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Architect blueprint creation successful:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Architect blueprint creation failed with exit code {e.returncode}:\n{e.stderr}")
        except FileNotFoundError as e:
            logger.error(f"Command not found: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Architect handoff: {e}")

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