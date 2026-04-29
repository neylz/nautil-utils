import os
import shutil

from nautil.plugin import action
from nautil import Artifact


@action("cp")
def cp(artifact: Artifact, source_path: str, dest_path: str, overwrite: bool = True):
    """
    Copies a file or directory from source_path to dest_path within the artifact's workspace.

    @param source_path: The relative path to the source file or directory to copy.
    @param dest_path: The relative path to the destination where the file or directory should be copied.
    @param overwrite: Whether to overwrite the destination if it already exists (default: True).
    """

    def step(workspace: str):
        _source_path = artifact.parset(source_path)
        _dest_path = artifact.parset(dest_path)

        artifact.log(f"cp({_source_path} -> {_dest_path})")

        source_full_path = _source_path if os.path.isabs(_source_path) else os.path.join(workspace, _source_path)
        dest_full_path = _dest_path if os.path.isabs(_dest_path) else os.path.join(workspace, _dest_path)

        source_full_path = os.path.normpath(source_full_path)
        dest_full_path = os.path.normpath(dest_full_path)

        if not os.path.exists(source_full_path):
            raise FileNotFoundError(f"Source path not found: {_source_path}")

        if os.path.isdir(dest_full_path):
            dest_full_path = os.path.join(dest_full_path, os.path.basename(source_full_path))

        dest_parent = os.path.dirname(dest_full_path)
        if dest_parent:
            os.makedirs(dest_parent, exist_ok=True)

        if os.path.exists(dest_full_path):
            if not overwrite:
                raise FileExistsError(f"Destination already exists: {_dest_path}")
            if os.path.isdir(dest_full_path):
                shutil.rmtree(dest_full_path)
            else:
                os.remove(dest_full_path)

        if os.path.isdir(source_full_path):
            shutil.copytree(source_full_path, dest_full_path)
        else:
            shutil.copy2(source_full_path, dest_full_path)

    return step
