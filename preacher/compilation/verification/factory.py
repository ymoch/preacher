from typing import Optional

from pluggy import PluginManager

from preacher.compilation.extraction import create_extraction_compiler
from preacher.plugin.manager import get_plugin_manager
from .description import DescriptionCompiler
from .matcher import MatcherFactoryCompiler
from .predicate import PredicateCompiler
from .response import ResponseDescriptionCompiler


def create_matcher_factory_compiler(
    plugin_manager: Optional[PluginManager] = None,
) -> MatcherFactoryCompiler:
    compiler = MatcherFactoryCompiler()

    plugin_manager = plugin_manager or get_plugin_manager()
    plugin_manager.hook.preacher_add_matchers(compiler=compiler)

    return compiler


def create_predicate_compiler(
    plugin_manager: Optional[PluginManager] = None,
) -> PredicateCompiler:
    matcher_factory = create_matcher_factory_compiler(plugin_manager=plugin_manager)
    return PredicateCompiler(matcher_factory)


def create_description_compiler(
    predicate: Optional[PredicateCompiler] = None,
    plugin_manager: Optional[PluginManager] = None,
) -> DescriptionCompiler:
    predicate = predicate or create_predicate_compiler(plugin_manager=plugin_manager)
    extraction = create_extraction_compiler(plugin_manager=plugin_manager)

    return DescriptionCompiler(extraction=extraction, predicate=predicate)


def create_response_description_compiler(
    predicate: Optional[PredicateCompiler] = None,
    description: Optional[DescriptionCompiler] = None,
    plugin_manager: Optional[PluginManager] = None,
) -> ResponseDescriptionCompiler:
    predicate = predicate or create_predicate_compiler(plugin_manager=plugin_manager)
    description = description or create_description_compiler()

    return ResponseDescriptionCompiler(predicate=predicate, description=description)
