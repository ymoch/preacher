from typing import Optional

from preacher.compilation.extraction import AnalysisCompiler, ExtractionCompiler
from preacher.plugin.manager import get_plugin_manager
from .description import DescriptionCompiler
from .matcher import MatcherFactoryCompiler
from .predicate import PredicateCompiler
from .response import ResponseDescriptionCompiler
from .response_body import ResponseBodyDescriptionCompiler


def create_matcher_factory_compiler() -> MatcherFactoryCompiler:
    compiler = MatcherFactoryCompiler()

    plugin_manager = get_plugin_manager()
    plugin_manager.hook.preacher_add_matchers(compiler=compiler)

    return compiler


def create_predicate_compiler() -> PredicateCompiler:
    matcher_factory = create_matcher_factory_compiler()
    return PredicateCompiler(matcher_factory)


def create_description_compiler(
    predicate: Optional[PredicateCompiler] = None,
) -> DescriptionCompiler:
    predicate = predicate or create_predicate_compiler()

    extraction = ExtractionCompiler()
    return DescriptionCompiler(extraction=extraction, predicate=predicate)


def create_response_description_compiler(
    predicate: Optional[PredicateCompiler] = None,
    description: Optional[DescriptionCompiler] = None,
) -> ResponseDescriptionCompiler:
    predicate = predicate or create_predicate_compiler()
    description = description or create_description_compiler()

    analysis = AnalysisCompiler()
    body = ResponseBodyDescriptionCompiler(
        analysis=analysis,
        description=description,
    )
    return ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        body=body,
    )
