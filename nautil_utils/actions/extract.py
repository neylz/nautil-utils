import os
import shutil

from nautil.plugin import action
from nautil import Artifact


@action("extract")
def extract(artifact: Artifact, archive_path: str, dest_path: str = ".", overwrite: bool = True):

    def step(workspace: str):
        print(f"extract({archive_path} -> {dest_path})")

        archive_full_path = archive_path if os.path.isabs(archive_path) else os.path.join(workspace, archive_path)
        dest_full_path = dest_path if os.path.isabs(dest_path) else os.path.join(workspace, dest_path)

        archive_full_path = os.path.normpath(archive_full_path)
        dest_full_path = os.path.normpath(dest_full_path)

        if not os.path.isfile(archive_full_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")

        if os.path.exists(dest_full_path):
            if not os.path.isdir(dest_full_path):
                raise NotADirectoryError(f"Destination is not a directory: {dest_path}")
            if not overwrite and os.listdir(dest_full_path):
                raise FileExistsError(f"Destination directory is not empty: {dest_path}")
        else:
            os.makedirs(dest_full_path, exist_ok=True)

        shutil.unpack_archive(archive_full_path, dest_full_path)

    return step
