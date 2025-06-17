import subprocess
import time

def main(test_mode=False):
    while True:
        try:
            # Execute the Orchestrator agent
            subprocess.run(['roo', '-m', 'orchestrator'])
        except Exception as e:
            print(f"Error executing orchestrator: {e}")
        
        # Sleep before next iteration or break
        if test_mode:
            time.sleep(10)  # Sleep before breaking in test mode
            break
        else:
            time.sleep(10)  # Wait before next iteration

if __name__ == '__main__':
    main()