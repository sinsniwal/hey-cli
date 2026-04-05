import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from hey_cli.runner import CommandRunner
from hey_cli.governance import GovernanceEngine

class TestCommandRunnerHandoff(unittest.TestCase):
    def setUp(self):
        self.gov = MagicMock(spec=GovernanceEngine)
        self.runner = CommandRunner(governance=self.gov)
        self.handoff_path = os.path.expanduser("~/.hey_cwd_handoff")
        if os.path.exists(self.handoff_path):
            os.remove(self.handoff_path)

    def tearDown(self):
        if os.path.exists(self.handoff_path):
            os.remove(self.handoff_path)

    @patch("subprocess.run")
    def test_run_command_captures_pwd(self, mock_run):
        # Simulate a command that includes the HEY_CWD_HANDOFF marker
        mock_result = MagicMock()
        mock_result.returncode = 0
        # Mocking the output of '(cd /tmp) ; printf "\nHEY_CWD_HANDOFF:%s\n" "$(pwd)"'
        mock_result.stdout = "some output\nHEY_CWD_HANDOFF:/tmp\n"
        mock_run.return_value = mock_result

        code, out = self.runner.run_command("cd /tmp", capture_pwd=True)

        # Verify the handoff file was created with the correct path
        self.assertTrue(os.path.exists(self.handoff_path))
        with open(self.handoff_path, "r") as f:
            self.assertEqual(f.read().strip(), "/tmp")
        
        # Verify the marker was stripped from the output
        self.assertEqual(out.strip(), "some output")

        # Verify the command was wrapped correctly
        mock_run.assert_called_once()
        called_cmd = mock_run.call_args[0][0]
        self.assertIn("HEY_CWD_HANDOFF", called_cmd)

    @patch("subprocess.run")
    def test_run_command_no_capture_pwd(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "normal output\n"
        mock_run.return_value = mock_result

        code, out = self.runner.run_command("ls", capture_pwd=False)

        self.assertFalse(os.path.exists(self.handoff_path))
        self.assertEqual(out.strip(), "normal output")
        
        # Verify the command was NOT wrapped
        mock_run.assert_called_once_with(
            "ls", shell=True, stdout=-1, stderr=-2, text=True
        )

    @patch("platform.system")
    @patch("subprocess.run")
    def test_run_command_windows_handoff(self, mock_run, mock_platform):
        mock_platform.return_value = "Windows"
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "some output\nHEY_CWD_HANDOFF:C:\\Temp\n"
        mock_run.return_value = mock_result

        # We need to mock os.getcwd and os.path.normpath to match Windows style in this test
        with patch("os.getcwd", return_value="C:\\Users\\Test"), \
             patch("os.path.expanduser", return_value=self.handoff_path):
            
            code, out = self.runner.run_command("cd C:\\Temp", capture_pwd=True)

            # Verify the command was wrapped using Windows CMD syntax
            called_cmd = mock_run.call_args[0][0]
            self.assertEqual(called_cmd, '("cd C:\\Temp") & echo. & echo HEY_CWD_HANDOFF:%CD%')

            # Verify the handoff file was created
            self.assertTrue(os.path.exists(self.handoff_path))
            with open(self.handoff_path, "r") as f:
                self.assertEqual(f.read().strip(), "C:\\Temp")

if __name__ == "__main__":
    unittest.main()
