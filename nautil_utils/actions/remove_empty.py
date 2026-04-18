import os

from nautil.plugin import action
from nautil import Artifact


@action("remove_empty")
def remove_empty(artifact: Artifact, files=True, dirs=True):
    """Removes empty (0b) files and/or directories (not containing any files) from the artifact's workspace."""
    
    def step(workspace):
        print("remove_empty")

        for root, dirs, files in os.walk(workspace, topdown=False):
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
