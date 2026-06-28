import os

from inspect import signature
from pathlib import Path
from typing import Union

# A path-like value that also accepts a plain string.
PathStr = Union[str, os.PathLike]

# Annotations that should be widened to also accept str.
_PATH_TYPES = (os.PathLike, Path)
_PATH_NAMES = {"PathLike", "os.PathLike", "Path", "pathlib.Path"}


def _is_path_annotation(annotation) -> bool:
    if isinstance(annotation, str):
        return annotation in _PATH_NAMES
    try:
        return annotation in _PATH_TYPES
    except TypeError:
        return False


def pathstroverload(func):
    """
    Widen ``PathLike``/``Path`` parameter annotations so they also accept ``str``.

    Decorate any function whose path parameters are annotated as ``PathLike`` (or
    ``Path``) and they will be reported as :data:`PathStr` (``str | os.PathLike``)
    instead. The runtime behaviour of the function is left untouched.
    """

    try:
        sig = signature(func)
    except (ValueError, TypeError):
        return func

    new_params = []
    changed = False
    for name, param in sig.parameters.items():
        if _is_path_annotation(param.annotation):
            param = param.replace(annotation=PathStr)
            func.__annotations__[name] = PathStr
            changed = True
        new_params.append(param)

    if changed:
        func.__signature__ = sig.replace(parameters=new_params)

    return func
