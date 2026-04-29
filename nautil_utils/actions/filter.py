import os
import shutil

from nautil.plugin import action
from nautil import Artifact

from nautil_utils.types import FilePredicate


def _to_predicate_args(relative_path: str):
    normalized = relative_path.replace("\\", "/")
    if "/" in normalized:
        file_path, file_name = normalized.rsplit("/", 1)
        if file_path:
            file_path = f"{file_path}/"
    else:
        file_name = normalized
        file_path = ""
    return file_name, file_path


@action("filter")
def filter(artifact: Artifact, filter_func: FilePredicate, root: str = ".") -> function:
    """
    Filters files and directories in the artifact's workspace based on a given predicate.

    @param filter_func: A function that takes file_name, file_path and workspace and returns True if the file/directory should be deleted, False otherwise.
    @param root: The relative path to the root directory within the workspace to start filtering from (default: "."). Only files and directories under this root will be considered for filtering.
    """

    def step(workspace: str):
        _root = artifact.parset(root)

        artifact.log("filter(root={}, filter_func={})".format(_root, filter_func.__name__))
        dirs_to_delete = []
        start_path = os.path.abspath(os.path.join(workspace, _root))
        workspace_path = os.path.abspath(workspace)

        if os.path.commonpath([workspace_path, start_path]) != workspace_path:
            raise ValueError(f"root must be within workspace: {_root}")

        if not os.path.isdir(start_path):
            return

        for current_root, dirs, _ in os.walk(start_path, topdown=False):
            for dir_name in dirs:
                dir_full_path = os.path.join(current_root, dir_name)
                dir_relative_path = os.path.relpath(dir_full_path, workspace)
                file_name, file_path = _to_predicate_args(dir_relative_path)
                if filter_func(file_name, file_path, workspace):
                    dirs_to_delete.append(dir_full_path)

        for dir_path in dirs_to_delete:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path, ignore_errors=True)

        for current_root, _, files in os.walk(start_path):
            for file in files:
                full_path = os.path.join(current_root, file)
                relative_path = os.path.relpath(full_path, workspace)
                file_name, file_path = _to_predicate_args(relative_path)
                if filter_func(file_name, file_path, workspace) and os.path.isfile(full_path):
                    os.remove(full_path)

    
    return step
