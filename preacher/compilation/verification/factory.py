from typing import Optional

from preacher.compilation.extraction import AnalysisCompiler, ExtractionCompiler
from .description import DescriptionCompiler
from .matcher import MatcherFactoryCompiler, add_default_matchers
from .predicate import PredicateCompiler
from .response import ResponseDescriptionCompiler
from .response_body import ResponseBodyDescriptionCompiler


def create_predicate_compiler() -> PredicateCompiler:
    matcher_factory = MatcherFactoryCompiler()
    add_default_matchers(matcher_factory)
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
