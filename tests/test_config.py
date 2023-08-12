import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import logging
from github import Github
from github import Auth
import config

class TestConfig(unittest.TestCase):


    def test_configure_github_api(self):
        # Set up mocks
        github_token = os.environ.get("MOCK_GITHUB_TOKEN")

        # Call the function
        result = config.configure_github_api(github_token)

        # Assert the expected result based on your test case
        self.assertEqual(result.get_user().id, 30549284)

    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"})
    def test_configure_logging_with_string_level(self):
        with patch('logging.basicConfig') as mock_basic_config:
            logger = config.configure_logging()
            
            mock_basic_config.assert_called_once_with(level=logging.DEBUG, format='%(asctime)s - [%(levelname)s] - %(message)s')
            self.assertEqual(logger.name, "default_logger")
    @patch.dict(os.environ, {"LOG_LEVEL": "1"})
    def test_configure_logging_with_integer_level(self):
        with patch('logging.basicConfig') as mock_basic_config:
            logger = config.configure_logging()
            
            mock_basic_config.assert_called_once_with(level=logging.ERROR, format='%(asctime)s - [%(levelname)s] - %(message)s')
            self.assertEqual(logger.name, "default_logger")

if __name__ == "__main__":
    unittest.main()
