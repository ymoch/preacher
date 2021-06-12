from logging import Logger
from typing import Optional

from pluggy import PluginManager
from yamlen import Loader

from preacher.core.logger import default_logger


def create_loader(
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> Loader:
    logger = logger or default_logger

    loader = Loader()
    if plugin_manager:
        plugin_manager.hook.preacher_modify_yaml_loader(loader=loader)
    else:
        logger.debug("No plugin manager is given. The built-in YAML tags are not available.")
    return loader
