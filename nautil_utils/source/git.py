
from os import PathLike
import os
import shutil
from pathlib import Path
import git
import tempfile

from nautil.core import Source


class GitSource(Source):
    def __init__(self, git_url: str, branch: str = "main", specific_commit: str = None, depth: int = 1):
        self.git_url = git_url
        self.branch = branch
        self.specific_commit = specific_commit
        self.depth = depth

    def copy_files(self, dest: PathLike, src_path: PathLike, overwrite: bool = False):
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = git.Repo.clone_from(self.git_url, tmp_dir, branch=self.branch, depth=self.depth)

            if self.specific_commit:
                repo.git.checkout(self.specific_commit)

            source_path = Path(tmp_dir) / src_path
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
                        for current_root, dir_names, file_names in os.walk(source_path):
                            dir_names[:] = [dir_name for dir_name in dir_names if dir_name != ".git"]
                            relative_root = Path(current_root).relative_to(source_path)
                            target_root = dest_path / relative_root
                            for file_name in file_names:
                                if file_name == ".git":
                                    continue
                                candidate = target_root / file_name
                                if candidate.exists():
                                    raise FileExistsError(f"Destination already exists: {candidate}")
                        shutil.copytree(
                            source_path,
                            dest_path,
                            dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(".git"),
                        )
                        return

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(
                    source_path,
                    dest_path,
                    ignore=shutil.ignore_patterns(".git"),
                )
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

