import re
from os import path
from typing import List, Pattern, Tuple

from nautil_us.types import FileNamePredicate


def _normalize_posix_path(file_path: str) -> str:
    normalized = file_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def _glob_to_regex(pattern: str) -> str:
    regex_parts = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if char == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                regex_parts.append(".*")
                i += 2
                continue
            regex_parts.append("[^/]*")
            i += 1
            continue
        if char == "?":
            regex_parts.append("[^/]")
            i += 1
            continue
        regex_parts.append(re.escape(char))
        i += 1
    return "".join(regex_parts)


def _compile_rule(pattern: str) -> Pattern[str]:
    anchored = pattern.startswith("/")
    if anchored:
        pattern = pattern[1:]

    directory_only = pattern.endswith("/")
    if directory_only:
        pattern = pattern.rstrip("/")

    if not pattern:
        return re.compile(r"^$")

    translated = _glob_to_regex(pattern)
    has_slash = "/" in pattern

    if anchored:
        prefix = "^"
    elif has_slash:
        prefix = r"^(?:.*/)?"
    else:
        prefix = r"^(?:.*/)?"

    if directory_only:
        suffix = r"(?:/.*)?$"
    elif has_slash:
        suffix = "$"
    else:
        suffix = r"$"

    return re.compile(prefix + translated + suffix)


def _load_rules(ignore_file_path: str) -> List[Tuple[bool, Pattern[str]]]:
    rules: List[Tuple[bool, Pattern[str]]] = []
    if not path.isfile(ignore_file_path):
        return rules

    with open(ignore_file_path, "r", encoding="utf-8") as ignore_file:
        for raw_line in ignore_file:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#") and not line.startswith(r"\#"):
                continue

            negated = False
            if line.startswith("!") and not line.startswith(r"\!"):
                negated = True
                line = line[1:]
            elif line.startswith(r"\!") or line.startswith(r"\#"):
                line = line[1:]

            if not line:
                continue

            rules.append((negated, _compile_rule(line)))

    return rules


def make_dotignore_predicate(ignore_file_name: str, workspace_relative: bool = True) -> FileNamePredicate:
    """
    Creates a predicate function that checks if a file should be ignored based on a .ignore file.

    :param ignore_file_name: The name of the .ignore file to look for (e.g., ".gitignore").
    :param workspace_relative: If True, the provided ``ignore_file_name`` is relative to the workspace root. If False, it is an absolute path or relative to the script.

    ## Example Usage
    ```
        from nautil_us.filter import make_dotignore_predicate

        # Create a predicate function based on a .gitignore file in the workspace
        predicate = make_dotignore_predicate(".packignore")

        # Use the predicate to check if a file should be ignored
        artifact = Artifact(...)\\
            .use(...)\\
            .filter_name(predicate)\\
            .output()
    ```
    """
    cached_workspace = None
    cached_rules: List[Tuple[bool, Pattern[str]]] = []

    def predicate(file_name: str, workspace: str) -> bool:
        nonlocal cached_workspace, cached_rules

        ignore_file_path = (
            path.join(workspace, ignore_file_name)
            if workspace_relative
            else path.abspath(ignore_file_name)
        )

        if cached_workspace != workspace:
            cached_workspace = workspace
            cached_rules = _load_rules(ignore_file_path)

        if not cached_rules:
            return False

        if path.isabs(file_name):
            try:
                file_name = path.relpath(file_name, workspace)
            except ValueError:
                file_name = path.basename(file_name)

        file_path = _normalize_posix_path(file_name)

        ignored = False
        for negated, rule in cached_rules:
            if rule.match(file_path):
                ignored = not negated

        return ignored

    return predicate

