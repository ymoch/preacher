from .analysis import AnalysisCompiler
from .body_description import BodyDescriptionCompiler
from .case import CaseCompiler
from .analysis_description import AnalysisDescriptionCompiler
from .extraction import ExtractionCompiler
from .predicate import PredicateCompiler
from .request import RequestCompiler
from .response_description import ResponseDescriptionCompiler
from .scenario import ScenarioCompiler


def create_compiler() -> ScenarioCompiler:
    request = RequestCompiler()

    extraction = ExtractionCompiler()
    analysis = AnalysisCompiler()
    predicate = PredicateCompiler()
    description = AnalysisDescriptionCompiler(
        extraction_compiler=extraction,
        predicate_compiler=predicate,
    )
    body_description = BodyDescriptionCompiler(
        analysis=analysis,
        description=description,
    )
    response = ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        body=body_description,
    )
    case = CaseCompiler(
        request=request,
        response=response,
    )
    scenario_compiler = ScenarioCompiler(
        description=description,
        case=case,
    )

    return scenario_compiler
