import pkgutil
import importlib

__all__ = []
pkg_name = __name__

# dynamically import all submodules
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    full_module_name = f"{pkg_name}.{module_name}"
    importlib.import_module(full_module_name)
    __all__.append(module_name)