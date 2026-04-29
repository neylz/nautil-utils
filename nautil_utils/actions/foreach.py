import inspect
import os

from typing import Callable, Any

from nautil.plugin import action
from nautil import Artifact

from nautil_utils.types import FilePredicate


def _is_within_workspace(workspace_path: str, target_path: str) -> bool:
    return os.path.commonpath([workspace_path, target_path]) == workspace_path


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


@action("foreach")
def foreach(
    artifact: Artifact,
    filter_func: FilePredicate,
    item_action: Callable[..., Any],
    root: str = ".",
    files: bool = True,
    dirs: bool = False,
    recursive: bool = True,
):
    """
    Applies an action for each file/directory matching a predicate.

    @param filter_func: Predicate receiving (file_name, file_path, workspace) and returning True when the path should be processed.
    @param item_action: Callable that accepts one of these signatures:
        (relative_path), (relative_path, workspace),
        (file_name, file_path), (file_name, file_path, workspace).
        If it returns a callable, that callable is treated as a Nautil step and called with workspace.
    @param root: Relative path inside the workspace used as traversal root (default: ".").
    @param files: Whether to include files (default: True).
    @param dirs: Whether to include directories (default: False).
    @param recursive: Whether to process subfolders recursively (default: True).
    """

    def run_item_action(relative_path: str, workspace: str):
        signature = inspect.signature(item_action)
        file_name, file_path = _to_predicate_args(relative_path)

        try:
            signature.bind(file_name, file_path, workspace)
            result = item_action(file_name, file_path, workspace)
        except TypeError:
            try:
                signature.bind(file_name, file_path)
                result = item_action(file_name, file_path)
            except TypeError:
                try:
                    signature.bind(relative_path, workspace)
                    result = item_action(relative_path, workspace)
                except TypeError:
                    try:
                        signature.bind(relative_path)
                    except TypeError as exc:
                        raise TypeError(
                            "item_action must accept one of: (relative_path), (relative_path, workspace), "
                            "(file_name, file_path), (file_name, file_path, workspace)"
                        ) from exc
                    result = item_action(relative_path)

        if callable(result):
            result(workspace)

    def step(workspace: str):
        artifact.log(f"foreach({root})")

        workspace_path = os.path.abspath(workspace)
        start_path = os.path.abspath(os.path.join(workspace_path, root))

        if not _is_within_workspace(workspace_path, start_path):
            raise ValueError(f"root must be within workspace: {root}")

        if not os.path.exists(start_path):
            return

        matching_paths = []

        if os.path.isfile(start_path):
            if files:
                rel_path = os.path.relpath(start_path, workspace_path)
                file_name, file_path = _to_predicate_args(rel_path)
                if filter_func(file_name, file_path, workspace):
                    matching_paths.append(rel_path)
        elif os.path.isdir(start_path):
            for current_root, walk_dirs, walk_files in os.walk(start_path):
                if dirs:
                    for dir_name in walk_dirs:
                        dir_full_path = os.path.join(current_root, dir_name)
                        rel_path = os.path.relpath(dir_full_path, workspace_path)
                        file_name, file_path = _to_predicate_args(rel_path)
                        if filter_func(file_name, file_path, workspace):
                            matching_paths.append(rel_path)

                if files:
                    for file_name in walk_files:
                        file_full_path = os.path.join(current_root, file_name)
                        rel_path = os.path.relpath(file_full_path, workspace_path)
                        candidate_name, file_path = _to_predicate_args(rel_path)
                        if filter_func(candidate_name, file_path, workspace):
                            matching_paths.append(rel_path)

                if not recursive:
                    break

        for relative_path in matching_paths:
            run_item_action(relative_path, workspace)

    return step
