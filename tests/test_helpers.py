import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import helpers
import subprocess
from unittest.mock import Mock

def test_contains_filtered_dirnames():
    filename = "path/to/exclude/some_file.txt"
    excluded_dirnames = ["exclude", "ignore"]
    result = helpers.contains_filtered_dirnames(filename, excluded_dirnames)
    assert result is True

def test_does_not_contain_filtered_dirnames():
    filename = "path/to/some_file.txt"
    excluded_dirnames = ["exclude", "ignore"]
    result = helpers.contains_filtered_dirnames(filename, excluded_dirnames)
    assert result is False

def test_extract_path_from_command():
    logger_mock = Mock()
    command = "some_command -p path/to/work"
    result = helpers.extract_path_from_command(logger_mock, command)
    assert result == "path/to/work"

def test_format_command_with_terraform():
    command = "apply -p path/to/work"
    iac_tool = "TERRAFORM"
    result = helpers.format_command(command, iac_tool)
    assert "-auto-approve" in result

def test_format_command_with_terragrunt():
    command = "apply -p path/to/work"
    iac_tool = "TERRAGRUNT"
    result = helpers.format_command(command, iac_tool)
    assert "--terragrunt-non-interactive" in result
