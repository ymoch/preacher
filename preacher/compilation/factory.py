from .analysis import AnalysisCompiler
from .body import BodyDescriptionCompiler
from .case import CaseCompiler
from .description import DescriptionCompiler
from .extraction import ExtractionCompiler
from .predicate import PredicateCompiler
from .request import RequestCompiler
from .response import ResponseDescriptionCompiler
from .scenario import ScenarioCompiler


def create_compiler() -> ScenarioCompiler:
    request = RequestCompiler()

    extraction = ExtractionCompiler()
    analysis = AnalysisCompiler()
    predicate = PredicateCompiler()
    description = DescriptionCompiler(
        extraction_compiler=extraction,
        predicate_compiler=predicate,
    )
    body_description = BodyDescriptionCompiler(
        analysis_compiler=analysis,
        description_compiler=description,
    )
    response = ResponseDescriptionCompiler(
        predicate_compiler=predicate,
        description_compiler=description,
        body_description_compiler=body_description,
    )
    case = CaseCompiler(
        request_compiler=request,
        response_compiler=response,
    )
    scenario_compiler = ScenarioCompiler(
        description=description,
        case=case,
    )

    return scenario_compiler
