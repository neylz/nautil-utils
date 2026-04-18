import os

from nautil.plugin import action
from nautil import Artifact


@action("touch")
def touch(artifact: Artifact, file_path: str, create_parents: bool = True):

    def step(workspace: str):
        print(f"touch({file_path})")

        full_path = file_path if os.path.isabs(file_path) else os.path.join(workspace, file_path)
        full_path = os.path.normpath(full_path)

        parent_dir = os.path.dirname(full_path)
        if create_parents and parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(full_path, "a", encoding="utf-8"):
            os.utime(full_path, None)

    return step
