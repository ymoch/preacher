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
