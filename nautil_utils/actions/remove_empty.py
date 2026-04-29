import os

from typing import List

from nautil.plugin import action
from nautil import Artifact


@action("remove_empty")
def remove_empty(artifact: Artifact, relative_paths: List[str] = [], files=True, dirs=True):
    """
    Removes empty (0b) files and/or directories (not containing any files) from the artifact's workspace.
    
    @param relative_paths: List of relative paths to check for empty files/directories. (default: []) If left empty, the entire workspace will be checked.
    @param files: Whether to remove empty files (default: True).
    @param dirs: Whether to remove empty directories (default: True).
    """
    
    def step(workspace: str):
        _relative_paths = [artifact.parset(rel) for rel in relative_paths]

        artifact.log("remove_empty(relative_paths={}, files={}, dirs={})".format(_relative_paths, files, dirs))

        target_paths = _relative_paths or [workspace]
        dir_targets = []

        for target in target_paths:
            full_path = target if os.path.isabs(target) else os.path.join(workspace, target)
            full_path = os.path.normpath(full_path)

            if not os.path.exists(full_path):
                continue

            if os.path.isfile(full_path):
                if files and os.path.getsize(full_path) == 0:
                    os.remove(full_path)
                continue

            if os.path.isdir(full_path):
                dir_targets.append(full_path)

        for root in dir_targets:
            for current_root, directories, file_names in os.walk(root, topdown=False):
                if files:
                    for file_name in file_names:
                        file_path = os.path.join(current_root, file_name)
                        if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                            os.remove(file_path)

                if dirs:
                    for directory_name in directories:
                        dir_path = os.path.join(current_root, directory_name)
                        if os.path.isdir(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)

            if dirs and root != workspace and os.path.isdir(root) and not os.listdir(root):
                os.rmdir(root)


    return step
