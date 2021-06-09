from typing import Optional

from pluggy import PluginManager

from preacher.compilation.extraction import ExtractionCompiler


def create_extraction_compiler(
    plugin_manager: Optional[PluginManager] = None,
) -> ExtractionCompiler:
    compiler = ExtractionCompiler()
    if plugin_manager:
        plugin_manager.hook.preacher_add_extractions(compiler=compiler)
    return compiler
