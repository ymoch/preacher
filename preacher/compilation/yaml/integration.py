import itertools
import sys
from logging import Logger
from typing import Iterator, Optional, Sequence

from pluggy import PluginManager

from preacher.core.logger import default_logger
from .factory import create_loader


def load_from_paths(
    paths: Sequence[str],
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> Iterator[object]:
    logger = logger or default_logger
    loader = create_loader(plugin_manager=plugin_manager, logger=logger)

    if not paths:
        logger.info("No scenario file is given. Load scenarios from stdin.")
        return loader.load_all(sys.stdin)

    return itertools.chain.from_iterable(
        loader.load_all_from_path(_hook_loading(path, logger)) for path in paths
    )


def _hook_loading(path: str, logger: Logger) -> str:
    logger.debug("Load: %s", path)
    return path
