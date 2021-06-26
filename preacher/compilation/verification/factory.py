from logging import Logger
from typing import Optional

from pluggy import PluginManager

from preacher.compilation.extraction import ExtractionCompiler, create_extraction_compiler
from preacher.core.logger import default_logger
from .description import DescriptionCompiler
from .matcher import MatcherFactoryCompiler
from .predicate import PredicateCompiler
from .response import ResponseDescriptionCompiler


def create_matcher_factory_compiler(
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> MatcherFactoryCompiler:
    logger = logger or default_logger

    compiler = MatcherFactoryCompiler()
    if plugin_manager:
        plugin_manager.hook.preacher_add_matchers(compiler=compiler)
    else:
        logger.info("No plugin manager is given. The default matchers are not available.")
    return compiler


def create_predicate_compiler(
    matcher_factory: Optional[PluginManager] = None,
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> PredicateCompiler:
    matcher_factory = matcher_factory or create_matcher_factory_compiler(
        plugin_manager=plugin_manager,
        logger=logger,
    )
    return PredicateCompiler(matcher_factory)


def create_description_compiler(
    extraction: Optional[ExtractionCompiler] = None,
    predicate: Optional[PredicateCompiler] = None,
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> DescriptionCompiler:
    extraction = extraction or create_extraction_compiler(
        plugin_manager=plugin_manager,
        logger=logger,
    )
    predicate = predicate or create_predicate_compiler(
        plugin_manager=plugin_manager,
        logger=logger,
    )
    return DescriptionCompiler(extraction=extraction, predicate=predicate)


def create_response_description_compiler(
    predicate: Optional[PredicateCompiler] = None,
    description: Optional[DescriptionCompiler] = None,
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> ResponseDescriptionCompiler:
    predicate = predicate or create_predicate_compiler(
        plugin_manager=plugin_manager, logger=logger
    )
    description = description or create_description_compiler(
        predicate=predicate,
        plugin_manager=plugin_manager,
        logger=logger,
    )
    return ResponseDescriptionCompiler(predicate=predicate, description=description)
