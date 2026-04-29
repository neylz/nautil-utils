from re import Pattern

from nautil_utils.types import FilePredicate


def make_regex_predicate(pattern: Pattern) -> FilePredicate:
    def predicate(file_name: str, file_path: str, workspace: str) -> bool:
        relative_path = f"{file_path}{file_name}" if file_path else file_name
        return bool(pattern.match(relative_path))

    return predicate