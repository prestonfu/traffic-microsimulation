"""Appends github repository path to python."""

import os
import sys

# PLEASE PUT YOUR PATH TO THE REPOSITORY HERE.
__REPO_PATH = "Your path to the traffic-microsimulation repository"
UTILS_FOLDER_PATH = os.path.join(__REPO_PATH, "utils")
AIMSUN_FOLDER_PATH = os.path.join(__REPO_PATH, "aimsun_scripts")


if not __REPO_PATH:
    model.reportError(
        'append_github_path_to_python',
        "Please change __REPO_PATH to your local repository path.")

for path in [UTILS_FOLDER_PATH, AIMSUN_FOLDER_PATH]:
    if path not in sys.path:
        sys.path.append(path)

print('Done')
