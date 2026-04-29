import os
import shutil

from nautil.plugin import action
from nautil import Artifact


@action("move")
def move(artifact: Artifact, source_path: str, dest_path: str):
    """
    Moves a file or directory from source_path to dest_path within the artifact's workspace.
    
    @param source_path: The relative path to the source file or directory.
    @param dest_path: The relative path to the destination directory or file.
    """

    def step(workspace):
        _source_path = artifact.parset(source_path)
        _dest_path = artifact.parset(dest_path)

        artifact.log("move({} -> {})".format(_source_path, _dest_path))

        source_full_path = _source_path if os.path.isabs(_source_path) else os.path.join(workspace, _source_path)
        dest_full_path = _dest_path if os.path.isabs(_dest_path) else os.path.join(workspace, _dest_path)

        source_full_path = os.path.normpath(source_full_path)
        dest_full_path = os.path.normpath(dest_full_path)

        if not os.path.exists(source_full_path):
            raise FileNotFoundError(f"Source path not found: {_source_path}")

        # `mv src existing_dir` moves src inside existing_dir.
        if os.path.isdir(dest_full_path):
            dest_full_path = os.path.join(dest_full_path, os.path.basename(source_full_path))

        dest_parent = os.path.dirname(dest_full_path)
        if dest_parent:
            os.makedirs(dest_parent, exist_ok=True)

        if os.path.abspath(source_full_path) == os.path.abspath(dest_full_path):
            return

        # Keep move behavior predictable on Windows by replacing existing destination.
        if os.path.exists(dest_full_path):
            if os.path.isdir(dest_full_path):
                shutil.rmtree(dest_full_path)
            else:
                os.remove(dest_full_path)

        shutil.move(source_full_path, dest_full_path)


    return step