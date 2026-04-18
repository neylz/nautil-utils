import os
import shutil

from nautil.plugin import action
from nautil import Artifact


@action("cp")
def cp(artifact: Artifact, source_path: str, dest_path: str, overwrite: bool = True):

    def step(workspace: str):
        print(f"cp({source_path} -> {dest_path})")

        source_full_path = source_path if os.path.isabs(source_path) else os.path.join(workspace, source_path)
        dest_full_path = dest_path if os.path.isabs(dest_path) else os.path.join(workspace, dest_path)

        source_full_path = os.path.normpath(source_full_path)
        dest_full_path = os.path.normpath(dest_full_path)

        if not os.path.exists(source_full_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")

        if os.path.isdir(dest_full_path):
            dest_full_path = os.path.join(dest_full_path, os.path.basename(source_full_path))

        dest_parent = os.path.dirname(dest_full_path)
        if dest_parent:
            os.makedirs(dest_parent, exist_ok=True)

        if os.path.exists(dest_full_path):
            if not overwrite:
                raise FileExistsError(f"Destination already exists: {dest_path}")
            if os.path.isdir(dest_full_path):
                shutil.rmtree(dest_full_path)
            else:
                os.remove(dest_full_path)

        if os.path.isdir(source_full_path):
            shutil.copytree(source_full_path, dest_full_path)
        else:
            shutil.copy2(source_full_path, dest_full_path)

    return step
