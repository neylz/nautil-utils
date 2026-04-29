import os

from typing import List

from nautil.plugin import action
from nautil import Artifact


@action("keep")
def keep(artifact: Artifact, relative_paths: List[str], root: str = ".", files=True, dirs=True):
    """
    Removes all files and directories in the artifact's workspace except for the specified relative paths.
    Inversely to filter_name, this action keeps the specified paths and deletes everything else.
    
    @param relative_paths: List of relative paths to preserve. Subdirectories of these paths will also be preserved.
    @param root: The root directory to consider (default: "."). Eg. if root is "data/", only files and directories within that path will be processed.
    @param files: Whether to consider files (default: True).
    @param dirs: Whether to consider directories (default: True).
    """
    
    def step(workspace: str):
        _root = artifact.parset(root)
        _relative_paths = [artifact.parset(rel) for rel in relative_paths]

        artifact.log("keep(relative_paths={}, root={}, files={}, dirs={})".format(_relative_paths, _root, files, dirs))

        workspace_path = os.path.abspath(workspace)
        root_path = _root if os.path.isabs(_root) else os.path.join(workspace_path, _root)
        root_path = os.path.normpath(root_path)

        if not os.path.exists(root_path):
            artifact.log(f"Warning: root path '{_root}' does not exist. Skipping.")
            return

        if os.path.commonpath([workspace_path, root_path]) != workspace_path:
            raise ValueError(f"Root path '{_root}' must be inside the workspace")

        keep_paths = []
        for rel in _relative_paths:
            if os.path.isabs(rel):
                candidate = os.path.normpath(rel)
            else:
                # Support both workspace-relative and root-relative keep paths.
                workspace_candidate = os.path.normpath(os.path.join(workspace_path, rel))
                if os.path.commonpath([root_path, workspace_candidate]) == root_path:
                    candidate = workspace_candidate
                else:
                    candidate = os.path.normpath(os.path.join(root_path, rel))

            if os.path.commonpath([root_path, candidate]) != root_path:
                artifact.log(f"Warning: keep path '{rel}' is outside root '{_root}'. Skipping.")
                continue

            keep_paths.append(candidate)

        def should_keep_file(file_path: str) -> bool:
            for keep_path in keep_paths:
                if file_path == keep_path:
                    return True
                if os.path.commonpath([file_path, keep_path]) == keep_path:
                    return True
            return False

        def should_keep_dir(dir_path: str) -> bool:
            for keep_path in keep_paths:
                common = os.path.commonpath([dir_path, keep_path])
                if common == dir_path or common == keep_path:
                    return True
            return False

        for walk_root, walk_dirs, walk_files in os.walk(root_path, topdown=False):
            if files:
                for file_name in walk_files:
                    file_full_path = os.path.join(walk_root, file_name)
                    if not should_keep_file(file_full_path) and os.path.isfile(file_full_path):
                        os.remove(file_full_path)

            if dirs:
                for dir_name in walk_dirs:
                    dir_full_path = os.path.join(walk_root, dir_name)
                    if not should_keep_dir(dir_full_path) and os.path.isdir(dir_full_path):
                        os.rmdir(dir_full_path)

    return step
