import os
import shutil

from nautil.plugin import action
from nautil import Artifact


@action("extract")
def extract(artifact: Artifact, archive_path: str, dest_path: str = ".", overwrite: bool = True):
    """
    Extracts an archive file (e.g., .zip, .tar.gz) to a specified destination directory within the artifact's workspace.
    
    @param archive_path: The relative path to the archive file to extract.
    @param dest_path: The relative path to the destination directory where the archive should be extracted (default: current directory).
    @param overwrite: Whether to overwrite existing files in the destination directory (default: True). If False, an error will be raised if the destination directory is not empty.
    """

    def step(workspace: str):
        _archive_path = artifact.parset(archive_path)
        _dest_path = artifact.parset(dest_path)

        artifact.log(f"extract({_archive_path} -> {_dest_path})")

        archive_full_path = _archive_path if os.path.isabs(_archive_path) else os.path.join(workspace, _archive_path)
        dest_full_path = _dest_path if os.path.isabs(_dest_path) else os.path.join(workspace, _dest_path)

        archive_full_path = os.path.normpath(archive_full_path)
        dest_full_path = os.path.normpath(dest_full_path)

        if not os.path.isfile(archive_full_path):
            raise FileNotFoundError(f"Archive not found: {_archive_path}")

        if os.path.exists(dest_full_path):
            if not os.path.isdir(dest_full_path):
                raise NotADirectoryError(f"Destination is not a directory: {_dest_path}")
            if not overwrite and os.listdir(dest_full_path):
                raise FileExistsError(f"Destination directory is not empty: {_dest_path}")
        else:
            os.makedirs(dest_full_path, exist_ok=True)

        shutil.unpack_archive(archive_full_path, dest_full_path)

    return step
