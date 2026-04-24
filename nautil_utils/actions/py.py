import os
import subprocess
import sys
from typing import Optional

from nautil.plugin import action
from nautil import Artifact


@action("py")
def py(artifact: Artifact, script_path: str, execution_location: Optional[str] = None):
    """
    Executes a Python script located at the specified path within the artifact's workspace.

    @param script_path: The relative path to the Python script to execute.
    @param execution_location: The relative path to the artifact workspace where the script should be executed.
    """

    def step(workspace: str):
        print(f"py({script_path})")

        script_full_path = script_path if os.path.isabs(script_path) else os.path.join(workspace, script_path)
        script_full_path = os.path.normpath(script_full_path)

        if not os.path.isfile(script_full_path):
            raise FileNotFoundError(f"Script not found: {script_path}")

        if execution_location is None:
            execution_full_path = workspace
        else:
            execution_full_path = (
                execution_location
                if os.path.isabs(execution_location)
                else os.path.join(workspace, execution_location)
            )
            execution_full_path = os.path.normpath(execution_full_path)

        if not os.path.isdir(execution_full_path):
            raise NotADirectoryError(f"Execution location is not a directory: {execution_location}")

        subprocess.run([sys.executable, script_full_path], cwd=execution_full_path, check=True)

    return step
