from .request import create_request_compiler
from .scenario import ScenarioCompiler, CaseCompiler
from .verification import (
    create_predicate_compiler,
    create_description_compiler,
    create_response_description_compiler
)


def create_compiler() -> ScenarioCompiler:
    request = create_request_compiler()

    predicate = create_predicate_compiler()
    description = create_description_compiler(predicate=predicate)
    response = create_response_description_compiler(
        predicate=predicate,
        description=description,
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
