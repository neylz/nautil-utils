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
        _dir_path = artifact.parset(dir_path)

        artifact.log("mkdir(dir_path={}, parents={}, exist_ok={})".format(_dir_path, parents, exist_ok))

        full_path = _dir_path if os.path.isabs(_dir_path) else os.path.join(workspace, _dir_path)
        full_path = os.path.normpath(full_path)

        if parents:
            os.makedirs(full_path, exist_ok=exist_ok)
        else:
            os.mkdir(full_path)

    return step
