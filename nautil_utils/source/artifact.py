from os import PathLike
import shutil
from pathlib import Path
import os

from nautil.core import Artifact, Source

_SUPPORTED_COMPRESSED_FORMATS = {
    "zip": ".zip",
    "tar": ".tar",
    "gztar": ".tar.gz",
}

class ArtifactSource(Source):
    def __init__(self, artifact: Artifact, root: PathLike = ".", compressed_format: str = None):
        """
        Creates a source from an existing artifact.

        :param artifact: The artifact to use as a source.
        :param root: The relative path inside the artifact to use for the source. (default: ".")
        :param compressed_format: If provided, the artifact will be compressed into the specified format. one of "zip", "tar" or "gztar".

        """
        self.path = artifact.path
        self.root = root
        self.compressed_format = compressed_format


    def copy_files(self, dest: PathLike, src_path: PathLike, overwrite: bool = False):
        source_root = Path(self.path) / self.root
        if not source_root.is_dir():
            raise ValueError(f"Invalid artifact root: {self.root}. Resolved path '{source_root}' is not a directory.")

        source_path = source_root / src_path
        if not source_path.exists():
            raise ValueError(f"Invalid source path: {src_path}. Resolved path '{source_path}' does not exist.")

        if not self.compressed_format:
            dest_path = Path(dest)

            if source_path.is_dir():
                if dest_path.exists():
                    if dest_path.is_file():
                        if not overwrite:
                            raise FileExistsError(f"Destination already exists: {dest}")
                        dest_path.unlink()
                    elif overwrite:
                        shutil.rmtree(dest_path)
                    else:
                        for current_root, _, file_names in os.walk(source_path):
                            relative_root = Path(current_root).relative_to(source_path)
                            target_root = dest_path / relative_root
                            for file_name in file_names:
                                candidate = target_root / file_name
                                if candidate.exists():
                                    raise FileExistsError(f"Destination already exists: {candidate}")
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                        return

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source_path, dest_path)
                return

            if source_path.is_file():
                if dest_path.exists():
                    if dest_path.is_dir():
                        if not overwrite:
                            raise FileExistsError(f"Destination already exists: {dest}")
                        shutil.rmtree(dest_path)
                    else:
                        if not overwrite:
                            raise FileExistsError(f"Destination already exists: {dest}")
                        dest_path.unlink()

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                return

            raise ValueError(f"Invalid source path: {src_path}. Resolved path '{source_path}' cannot be copied.")
        
        if self.compressed_format not in _SUPPORTED_COMPRESSED_FORMATS.keys():
            raise ValueError(f"Unsupported compressed format: {self.compressed_format}. Supported formats are: {', '.join(_SUPPORTED_COMPRESSED_FORMATS.keys())}.")
        
        # ensure output has the correct extension
        extension = _SUPPORTED_COMPRESSED_FORMATS[self.compressed_format]
        dest_str = str(dest)
        archive_path = dest_str if dest_str.endswith(extension) else f"{dest_str}{extension}"
        archive_target = Path(archive_path)

        if archive_target.exists():
            if not overwrite:
                raise FileExistsError(f"Destination already exists: {archive_target}")
            if archive_target.is_dir():
                shutil.rmtree(archive_target)
            else:
                archive_target.unlink()

        archive_target.parent.mkdir(parents=True, exist_ok=True)

        # make_archive expects a base path without extension.
        archive_base_name = archive_path[:-len(extension)]

        if source_path.is_dir():
            root_dir = source_path
            base_dir = "."
        elif source_path.is_file():
            root_dir = source_path.parent
            base_dir = source_path.name
        else:
            raise ValueError(f"Invalid source path: {src_path}. Resolved path '{source_path}' cannot be archived.")

        shutil.make_archive(
            base_name=archive_base_name,
            format=self.compressed_format,
            root_dir=root_dir,
            base_dir=base_dir,
        )
