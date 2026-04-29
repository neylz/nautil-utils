from os import PathLike
import os
import shutil
from pathlib import Path

from nautil.core import Source


class LocalSource(Source):
    def __init__(self, path: PathLike):
        self.path = path

    def copy_files(self, dest: PathLike, src_path: PathLike, overwrite: bool = False):
        source_path = Path(self.path) / src_path
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

        raise ValueError(f"Invalid source path: {src_path}. Resolved path '{source_path}' does not exist.")

