import unittest
from unittest.mock import patch
import subprocess

class TestRunAutonomy(unittest.TestCase):
    @patch('subprocess.run')
    @patch('time.sleep')
    def test_core_loop_execution(self, mock_sleep, mock_run):
        """Test that the core loop executes the Orchestrator command"""
        # This test should fail initially since the functionality isn't implemented
        from run_autonomy import main
        main(test_mode=True)  # test_mode will run only one iteration
        
        mock_run.assert_called_once_with(['roo', '-m', 'orchestrator'])
        mock_sleep.assert_called_once_with(10)