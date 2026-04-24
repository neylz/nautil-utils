import os

from os import path
from typing import List, Optional

from nautil.plugin import action
from nautil import Artifact


@action("remove_empty")
def remove_empty(artifact: Artifact, relative_paths: Optional[List[str]] = None, files=True, dirs=True):
    """
    Removes empty (0b) files and/or directories (not containing any files) from the artifact's workspace.
    
    @param relative_paths: Optional list of relative paths to check for empty files/directories. If not provided, the entire workspace will be checked.
    @param files: Whether to remove empty files (default: True).
    @param dirs: Whether to remove empty directories (default: True).
    """
    
    def step(workspace):
        print("remove_empty")

        # If relative_paths is provided, use it; otherwise, walk the entire workspace
        if relative_paths is not None:
            walk_paths = [path.join(workspace, p) for p in relative_paths]
                
        else:
            walk_paths = [workspace]

        for wp in walk_paths:
            if not path.exists(wp):
                print(f"Warning: relative path '{path.relpath(wp, workspace)}' does not exist. Skipping.")
                continue

            for root, dirs, files in os.walk(wp, topdown=False):
                if dirs:
                    for dir_name in dirs:
                        dir_full_path = os.path.join(root, dir_name)
                        if dirs and not os.listdir(dir_full_path):
                            os.rmdir(dir_full_path)

            if files:
                for file_name in files:
                    file_full_path = os.path.join(root, file_name)
                    if files and os.path.isfile(file_full_path) and os.path.getsize(file_full_path) == 0:
                        os.remove(file_full_path)

    return step
