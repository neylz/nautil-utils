import os

from nautil.plugin import action
from nautil import Artifact


@action("mkdir")
def mkdir(artifact: Artifact, dir_path: str, parents: bool = True, exist_ok: bool = True):
    """
    Creates a directory at the specified path within the artifact's workspace.
    
    @param dir_path: The relative path to the directory to create.
    @param parents: Whether to create parent directories if they don't exist (default: True).
    @param exist_ok: Whether to raise an error if the directory already exists (default: True).
    """

    def step(workspace: str):
        print(f"mkdir({dir_path})")

        full_path = dir_path if os.path.isabs(dir_path) else os.path.join(workspace, dir_path)
        full_path = os.path.normpath(full_path)

        if parents:
            os.makedirs(full_path, exist_ok=exist_ok)
        else:
            os.mkdir(full_path)

    return step
