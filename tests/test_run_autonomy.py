import unittest
from unittest.mock import patch, MagicMock
import subprocess
import logging
import run_autonomy

class TestRunAutonomy(unittest.TestCase):
    @patch('run_autonomy.subprocess.run')
    @patch('run_autonomy.time.sleep')
    @patch('run_autonomy.logging.getLogger')
    def test_successful_execution(self, mock_logger, mock_sleep, mock_run):
        """Test successful orchestrator execution"""
        # Setup
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        mock_run.return_value = MagicMock(stdout="Success", stderr="")
        
        # Execute
        run_autonomy.main(test_mode=True)
        
        # Verify
        mock_run.assert_called_once_with(
            ['roo', '-m', 'orchestrator'],
            capture_output=True,
            text=True,
            check=True
        )
        mock_log.info.assert_any_call("Starting autonomous development loop")
        mock_log.info.assert_any_call("Orchestrator executed successfully:\nSuccess")
        mock_sleep.assert_not_called()  # Since test_mode breaks after first iteration

    @patch('run_autonomy.subprocess.run')
    @patch('run_autonomy.time.sleep')
    @patch('run_autonomy.logging.getLogger')
    def test_command_failure(self, mock_logger, mock_sleep, mock_run):
        """Test command execution failure"""
        # Setup
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=['roo', '-m', 'orchestrator'],
            stderr="Command failed"
        )
        
        # Execute
        run_autonomy.main(test_mode=True)
        
        # Verify
        mock_log.error.assert_called_with(
            "Orchestrator execution failed with exit code 1:\nCommand failed"
        )

    @patch('run_autonomy.subprocess.run')
    @patch('run_autonomy.time.sleep')
    @patch('run_autonomy.logging.getLogger')
    def test_command_not_found(self, mock_logger, mock_sleep, mock_run):
        """Test command not found error"""
        # Setup
        mock_log = MagicMock()
        mock_logger.return_value = mock_log
        mock_run.side_effect = FileNotFoundError("Command not found")
        
        # Execute
        run_autonomy.main(test_mode=True)
        
        # Verify
        mock_log.error.assert_called_with("Command not found: Command not found")