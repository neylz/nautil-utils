import os
import shutil

from nautil.plugin import action
from nautil import Artifact

from nautil_utils.types import FileNamePredicate


@action("filter_name")
def filter_name(artifact: Artifact, filter_func: FileNamePredicate) -> function:
    def step(workspace: str):
        print("filter_name")
        dirs_to_delete = []

        for root, dirs, _ in os.walk(workspace, topdown=False):
            for dir_name in dirs:
                dir_full_path = os.path.join(root, dir_name)
                dir_relative_path = os.path.relpath(dir_full_path, workspace)
                if filter_func(dir_relative_path, workspace):
                    dirs_to_delete.append(dir_full_path)

        for dir_path in dirs_to_delete:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path, ignore_errors=True)

        for root, _, files in os.walk(workspace):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, workspace)
                if filter_func(relative_path, workspace) and os.path.isfile(full_path):
                    os.remove(full_path)

    
    return step
