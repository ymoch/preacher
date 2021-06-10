from logging import Logger
from typing import Optional

from pluggy import PluginManager

from preacher.compilation.extraction import ExtractionCompiler
from preacher.core.logger import default_logger


def create_extraction_compiler(
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> ExtractionCompiler:
    logger = logger or default_logger
    compiler = ExtractionCompiler()
    if plugin_manager:
        plugin_manager.hook.preacher_add_extractions(compiler=compiler)
    else:
        message = "No plugin manager is given. The default extraction methods are not available."
        logger.info(message)
    return compiler
