from re import Pattern

from nautil_us.types import FileNamePredicate


def make_regex_predicate(pattern: Pattern, _: str) -> FileNamePredicate:
    def predicate(file_name: str, workspace: str) -> bool:
        return bool(pattern.match(file_name))

    return predicate