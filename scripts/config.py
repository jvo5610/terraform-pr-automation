import os
import logging
from github import Github
from github import Auth

def configure_github_api(github_token):
    auth = Auth.Token(github_token)
    g = Github(auth=auth)
    return g

def configure_logging():
    # Get the desired logging level from the environment variable (default to ERROR)
    log_level = os.environ.get("LOG_LEVEL", "ERROR")

    # Convert the string level to the corresponding logging level constant
    log_level = getattr(logging, log_level.upper(), None)
    if not isinstance(log_level, int):
        log_level = logging.ERROR

    # Configure the logger with the desired logging level
    logging.basicConfig(level=log_level, format='%(asctime)s - [%(levelname)s] - %(message)s')

    return logging.getLogger("default_logger")
   