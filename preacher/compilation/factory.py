from .case import CaseCompiler
from .request import RequestCompiler, RequestBodyCompiler
from .scenario import ScenarioCompiler
from .verification import (
    AnalysisCompiler,
    DescriptionCompiler,
    ExtractionCompiler,
    PredicateCompiler,
    ResponseDescriptionCompiler,
    ResponseBodyDescriptionCompiler,
)


def create_compiler() -> ScenarioCompiler:
    request_body = RequestBodyCompiler()
    request = RequestCompiler(body=request_body)

    extraction = ExtractionCompiler()
    analysis = AnalysisCompiler()
    predicate = PredicateCompiler()
    description = DescriptionCompiler(
        extraction=extraction,
        predicate=predicate,
    )
    response_body_description = ResponseBodyDescriptionCompiler(
        analysis=analysis,
        description=description,
    )
    response = ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        body=response_body_description,
    )
    case = CaseCompiler(
        request=request,
        response=response,
        description=description,
    )
    scenario_compiler = ScenarioCompiler(
        description=description,
        case=case,
    )

    return scenario_compiler
