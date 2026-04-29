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
        _script_path = artifact.parset(script_path)
        _execution_location = artifact.parset(execution_location) if execution_location is not None else None

        artifact.log("py(script_path={}, execution_location={})".format(_script_path, _execution_location))

        script_full_path = _script_path if os.path.isabs(_script_path) else os.path.join(workspace, _script_path)
        script_full_path = os.path.normpath(script_full_path)

        if not os.path.isfile(script_full_path):
            raise FileNotFoundError(f"Script not found: {script_path}")

        if execution_location is None:
            execution_full_path = workspace
        else:
            execution_full_path = (
                _execution_location
                if os.path.isabs(_execution_location)
                else os.path.join(workspace, _execution_location)
            )
            execution_full_path = os.path.normpath(execution_full_path)

        if not os.path.isdir(execution_full_path):
            raise NotADirectoryError(f"Execution location is not a directory: {execution_location}")

        subprocess.run([sys.executable, script_full_path], cwd=execution_full_path, check=True)

    return step
