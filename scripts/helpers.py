import subprocess

def str_to_bool(s):
    return s.lower() == "true"

def contains_filtered_dirnames(filename, excluded_dirnames):
    for dirname in excluded_dirnames:
        if dirname in filename:
            return True
    return False

def extract_path_from_command(logger, command):
    # Split the command into separate words
    words = command.split()

    # Find the index of the "-p" option
    try:
        index = words.index("-p")
    except Exception as e:
        logger.warning("Working path not provided, using root path")
        logger.warning(f"Warning: {str(e)}")
        return ""

    # Return the word that follows the "-p" option
    if index + 1 < len(words):
        return words[index + 1]

def format_command(logger, command, iac_tool, is_reviewed, review_required, review_paths):
    AUTO_APPROVE_COMMANDS = ["apply", "destroy"]
    # Extract the path and words before -p
    paths_set = set()
    words = command.split()
    index = words.index("-p") if "-p" in words else None
    command_words = words[:index] if index is not None else words
    paths = words[index + 1] if index is not None and index + 1 < len(words) else None
    if paths:
        paths_set = set(paths.split('/'))

    # Convert the lists to sets for efficient comparison
    set1 = set(command_words)
    set2 = set(AUTO_APPROVE_COMMANDS)
    set3 = set(review_paths)

    paths_need_review = paths_set.intersection(set3)
    command_intersections = set1.intersection(set2)

    logger.debug(f"command: {command}")
    logger.debug(f"commands set: {set1}")
    logger.debug(f"paths set: {paths_set}")
    logger.debug(f"paths that need review set : {set3}")
    logger.debug(f"Path intersections: {paths_need_review}")
    logger.debug(f"Review required: {review_required}")
    logger.debug(f"Has reviews: {is_reviewed}")

    if command_intersections:
        if not is_reviewed and paths_need_review and review_required:
            raise ValueError("At least 1 review is required to run apply command")
        if iac_tool=="TERRAFORM":
            command_words.append("-auto-approve")
        if iac_tool=="TERRAGRUNT":
            command_words.append("-auto-approve")

    return command_words.append("--terragrunt-non-interactive")

def filter_files_by_depth(logger, files_list, depth, iac_tool, excluded_dirnames):
    if iac_tool == "TERRAGRUNT":
        return filter_terragrunt(logger, files_list, depth, excluded_dirnames)
    elif iac_tool == "TERRAFORM":
        return filter_terraform(files_list, excluded_dirnames)

def filter_terragrunt(logger, files_list, depth, excluded_dirnames):
    try:
        filtered_list = []
        for file in files_list:
            if "terragrunt.hcl" in file:
                subdirs = file.split('/')
                if "terragrunt.hcl" not in subdirs[depth]:
                    clean_path = '/'.join(subdirs[:-1])
                    if not contains_filtered_dirnames(file, excluded_dirnames):
                        filtered_list.append(clean_path)
        return filtered_list
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error("No files accomplish path depth")
        logger.error("List: %s", ', '.join(files_list))
        return []

def filter_terraform(files_list, excluded_dirnames):
    filtered_list = []
    for file in files_list:
        subdirs = file.split('/')
        clean_path = '/'.join(subdirs[:-1])
        if not contains_filtered_dirnames(file, excluded_dirnames):
            filtered_list.append(clean_path)
    unique_list = list(set(filtered_list))
    return unique_list

def run_commands(logger, command, working_directory):
    
    logger.debug("COMMAND: ")
    logger.debug(command)
    logger.debug("WORKING_DIRECTORY: "+working_directory)

    result = {}
  
    try:
        # Run the Terragrunt plan command and capture the output
        exec_command = subprocess.run(command, capture_output=True, text=True, check=True, cwd=working_directory)

        result["success"] = True
        result["output"] = exec_command.stdout
        print(exec_command)
        return result

    except subprocess.CalledProcessError as e:
        result["success"] = False
        result["output"] = e.stderr
        return result

def comment_pr(logger, pull_request, body, command, path):

    if path=="":
        path+="root_path"

    try:
        comment_body=f"###  Results for `{command}` on `{path}` \n\n"
        comment_body+="<details>\n"
        comment_body+="<summary>Show output</summary>\n\n"
        comment_body+="```diff\n"
        comment_body+=body
        comment_body+= "```\n\n"
        comment_body+="</details>"
        pull_request.create_issue_comment(comment_body)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        exit(1)

def comment_pr_message(logger, pull_request, body):

    try:
        comment_body=f"### `{body}` \n"
        pull_request.create_issue_comment(comment_body)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        exit(1)
