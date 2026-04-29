import os
import shutil

from nautil.plugin import action
from nautil import Artifact


@action("rm")
def rm(artifact: Artifact, target_path: str, recursive: bool = True, missing_ok: bool = True):
    """
    Removes a file or directory at the specified path within the artifact's workspace.
    
    @param target_path: The relative path to the file or directory to remove.
    @param recursive: Whether to remove directories recursively (default: True). If False, an error will be raised if the target is a non-empty directory.
    @param missing_ok: Whether to ignore the error if the target path does not exist (default: True).
    """

    def step(workspace: str):
        _target_path = artifact.parset(target_path)

        artifact.log("rm(target_path={}, recursive={}, missing_ok={})".format(_target_path, recursive, missing_ok))

        full_path = _target_path if os.path.isabs(_target_path) else os.path.join(workspace, _target_path)
        full_path = os.path.normpath(full_path)

        if not os.path.exists(full_path):
            if missing_ok:
                return
            raise FileNotFoundError(f"Path not found: {_target_path}")

        if os.path.isfile(full_path) or os.path.islink(full_path):
            os.remove(full_path)
            return

        if recursive:
            shutil.rmtree(full_path)
        else:
            os.rmdir(full_path)

    return step
