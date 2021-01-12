from typing import Optional

from pluggy import PluginManager

from preacher.compilation.extraction import ExtractionCompiler
from preacher.plugin.manager import get_plugin_manager


def create_extraction_compiler(
    plugin_manager: Optional[PluginManager] = None,
) -> ExtractionCompiler:
    compiler = ExtractionCompiler()

    plugin_manager = plugin_manager or get_plugin_manager()
    plugin_manager.hook.preacher_add_extractions(compiler=compiler)

    return compiler
