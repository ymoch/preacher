import sys
import types
import uuid
from importlib.util import spec_from_file_location, module_from_spec
from logging import Logger
from typing import Iterable

from pluggy import PluginManager

from preacher.core.logger import default_logger

__all__ = ["load_plugins"]


def load_plugins(
    manager: PluginManager,
    plugins: Iterable[str] = (),
    logger: Logger = default_logger,
) -> None:
    """
    Load plugins explicitly.

    Args:
        manager: A plugin manager to load plugins.
        plugins: Plugin paths to load.
        logger: A logger.
    Raises:
        RuntimeError: when a given plugin cannot be loaded as a module.
        Exception: when loading a plugin fails.
    """
    modules = (_load_module(path, logger) for path in plugins)
    for module in modules:
        manager.register(module)


def _load_module(path: str, logger: Logger) -> types.ModuleType:
    name = _unique_name()
    logger.info('Load module file "%s" as module name "%s"', path, name)

    spec = spec_from_file_location(name, path)
    if not spec:
        raise RuntimeError(f"Could not load as a module: {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    sys.modules[name] = module  # To enable sub-processes use this module.

    return module


def _unique_name() -> str:
    return str(uuid.uuid4())
