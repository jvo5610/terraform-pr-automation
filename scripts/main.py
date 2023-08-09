import os
import json
from config import configure_logging, configure_github_api
from helpers import extract_path_from_command, format_command, filter_files_by_depth, run_commands, comment_pr, comment_pr_message

GITHUB_CONTEXT=json.loads(os.environ.get("GITHUB_CONTEXT"))
EVENT_TYPE=GITHUB_CONTEXT.get("event_name")
EVENT=GITHUB_CONTEXT.get("event")
GITHUB_TOKEN=GITHUB_CONTEXT.get("token")
GITHUB_WORKSPACE=os.environ.get("GITHUB_WORKSPACE")
TERRAGRUNT_DEPTH=int(os.environ.get("TERRAGRUNT_DEPTH"))
IAC_TOOL=os.environ.get("IAC_TOOL").upper()
TERRAFORM_MODULES_DIRNAME=os.environ.get("TERRAFORM_MODULES_DIRNAME")

logger = configure_logging()
github = configure_github_api(GITHUB_TOKEN)
REPOSITORY = github.get_repo(GITHUB_CONTEXT.get("repository"))

def case_pull_request():
    logger.debug("Handling pull_request event...\n ")

    repo = REPOSITORY
    pr = repo.get_pull(EVENT.get("number"))

    # Get the files that were changed in the pull request
    changed_files = [file.filename for file in pr.get_files()]
    logger.debug("Changed files: %s", ', '.join(changed_files))

    filtered_paths = filter_files_by_depth(logger, changed_files, TERRAGRUNT_DEPTH, IAC_TOOL, TERRAFORM_MODULES_DIRNAME)
    logger.debug("Filtered paths: %s", ', '.join(filtered_paths))

    if len(filtered_paths) < 1:
        comment_pr_message(logger, pr, f"No files changed accomplish Terragrunt path depth defined in action [depth={TERRAGRUNT_DEPTH}]")

    # Command to execute
    command = []
    if IAC_TOOL == "TERRAFORM":
        command.extend(["terraform","plan"])
        command_init=["terraform", "init"]
    if IAC_TOOL == "TERRAGRUNT":
        command.extend(["terragrunt","run-all", "plan"])

    executions_results=[]

    for path in filtered_paths:
        # Specify the working directory
        working_directory = GITHUB_WORKSPACE+"/"+path

        if IAC_TOOL == "TERRAFORM":
             # Run init
            init_result = run_commands(logger, command_init, working_directory, IAC_TOOL)
            if init_result["success"]:
                # Print the command output
                logger.debug("Init output: "+init_result["output"])
            else:
                # Print error message and exit with non-zero status code
                logger.error("Init error: "+init_result["output"])
                comment_pr(logger, pr, init_result["output"], " ".join(init_command),path)
                continue

        # Run commands
        command_result = run_commands(logger, command, working_directory, IAC_TOOL)
        if command_result["success"]:
            # Print the command output
            logger.debug("Command output: "+command_result["output"])
            comment_pr(logger, pr, command_result["output"], " ".join(command),path)
        else:
            # Print error message and exit with non-zero status code
            logger.error("Command error: "+command_result["output"])
            comment_pr(logger, pr, command_result["output"], " ".join(command),path)

        executions_results.append(command_result["success"])

    if any(not value for value in executions_results):
        exit(1)


def case_issue_comment():
    logger.debug("Handling issue_comment event...\n ")
    
    comment_metadata=EVENT.get("comment", {})
    issue_metadata=EVENT.get("issue", {})

    repo = REPOSITORY
    pr = repo.get_pull(issue_metadata.get("number"))

    comment = pr.get_issue_comment(comment_metadata.get("id"))
    comment.create_reaction("rocket")
    
    logger.debug("COMMENT_BODY="+comment_metadata.get("body"))
    logger.debug("WORKSPACE="+GITHUB_WORKSPACE)

    # Command to execute
    command = format_command(comment_metadata.get("body"), IAC_TOOL)
    # Specify the working directory
    relative_path=extract_path_from_command(logger, comment_metadata.get("body"), IAC_TOOL)
    working_directory = GITHUB_WORKSPACE+"/"+relative_path

    # Run init if terraform
    if IAC_TOOL == "TERRAFORM":
        command_init=["terraform", "init"]
        init_result = run_commands(logger, command_init, working_directory, IAC_TOOL)
        if init_result["success"]:
            # Print the command output
            logger.debug("Init output: "+init_result["output"])
        else:
            # Print error message and exit with non-zero status code
            logger.error("Init error: "+init_result["output"])
            comment_pr(logger, pr, init_result["output"], " ".join(init_command),relative_path)
            exit(1)

    # Run commands
    command_result = run_commands(logger, command, working_directory, IAC_TOOL)
    if command_result["success"]:
        # Print the command output
        logger.debug("Command output: "+command_result["output"])
        comment_pr(logger, pr, command_result["output"], " ".join(command),relative_path)
    else:
        # Print error message and exit with non-zero status code
        logger.error("Command error: "+command_result["output"])
        comment_pr(logger, pr, command_result["output"], " ".join(command),relative_path)
        exit(1)

def default_case():
    logger.debug("Handling default...\n ")

try:

    if EVENT_TYPE == "pull_request":
        case_pull_request()
    elif EVENT_TYPE == "issue_comment":
        case_issue_comment()
    else:
        default_case()

except Exception as e:
    logger.error(f"Error: {str(e)}")
    exit(1)
