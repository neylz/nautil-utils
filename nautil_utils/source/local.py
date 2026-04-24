from os import PathLike
import shutil

from nautil.core import Source


class LocalSource(Source):
    def __init__(self, path: PathLike):
        self.path = path

    def copy_files(self, dest: PathLike):
        shutil.copytree(self.path, dest, dirs_exist_ok=True)

