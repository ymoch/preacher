from .request import create_request_compiler
from .scenario import ScenarioCompiler, CaseCompiler
from .verification import (
    AnalysisCompiler,
    DescriptionCompiler,
    ExtractionCompiler,
    PredicateCompiler,
    ResponseDescriptionCompiler,
    ResponseBodyDescriptionCompiler,
)


def create_compiler() -> ScenarioCompiler:
    request = create_request_compiler()

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
