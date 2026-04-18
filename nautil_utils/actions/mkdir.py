import os

from nautil.plugin import action
from nautil import Artifact


@action("mkdir")
def mkdir(artifact: Artifact, dir_path: str, parents: bool = True, exist_ok: bool = True):

    def step(workspace: str):
        print(f"mkdir({dir_path})")

        full_path = dir_path if os.path.isabs(dir_path) else os.path.join(workspace, dir_path)
        full_path = os.path.normpath(full_path)

        if parents:
            os.makedirs(full_path, exist_ok=exist_ok)
        else:
            os.mkdir(full_path)

    return step
