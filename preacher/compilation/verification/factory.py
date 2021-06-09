from typing import Optional

from pluggy import PluginManager

from preacher.compilation.extraction import ExtractionCompiler, create_extraction_compiler
from .description import DescriptionCompiler
from .matcher import MatcherFactoryCompiler
from .predicate import PredicateCompiler
from .response import ResponseDescriptionCompiler


def create_matcher_factory_compiler(
    plugin_manager: Optional[PluginManager] = None,
) -> MatcherFactoryCompiler:
    compiler = MatcherFactoryCompiler()
    if plugin_manager:
        plugin_manager.hook.preacher_add_matchers(compiler=compiler)
    return compiler


def create_predicate_compiler(
    plugin_manager: Optional[PluginManager] = None,
) -> PredicateCompiler:
    matcher_factory = create_matcher_factory_compiler(plugin_manager=plugin_manager)
    return PredicateCompiler(matcher_factory)


def create_description_compiler(
    extraction: Optional[ExtractionCompiler] = None,
    predicate: Optional[PredicateCompiler] = None,
    plugin_manager: Optional[PluginManager] = None,
) -> DescriptionCompiler:
    extraction = extraction or create_extraction_compiler(plugin_manager=plugin_manager)
    predicate = predicate or create_predicate_compiler(plugin_manager=plugin_manager)
    return DescriptionCompiler(extraction=extraction, predicate=predicate)


def create_response_description_compiler(
    predicate: Optional[PredicateCompiler] = None,
    description: Optional[DescriptionCompiler] = None,
    plugin_manager: Optional[PluginManager] = None,
) -> ResponseDescriptionCompiler:
    predicate = predicate or create_predicate_compiler(plugin_manager=plugin_manager)
    description = description or create_description_compiler(
        predicate=predicate,
        plugin_manager=plugin_manager,
    )
    return ResponseDescriptionCompiler(predicate=predicate, description=description)
