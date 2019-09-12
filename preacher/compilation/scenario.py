"""Scenario compilation."""

from collections.abc import Mapping
from functools import partial
from typing import Any, Optional

from preacher.core.scenario import Scenario
from preacher.core.case import Case
from .error import CompilationError
from .case import CaseCompiler
from .util import map_on_key, run_on_key


_KEY_LABEL = 'label'
_KEY_DEFAULT = 'default'
_KEY_CASES = 'cases'


class ScenarioCompiler:

    def __init__(self, case_compiler: Optional[CaseCompiler] = None):
        self._case_compiler = case_compiler or CaseCompiler()

    def compile(self, obj: Mapping) -> Scenario:
        label = obj.get(_KEY_LABEL)
        if label is not None and not isinstance(label, str):
            raise CompilationError(
                message='Must be a string',
                path=[_KEY_LABEL],
            )

        default = obj.get(_KEY_DEFAULT, {})
        if not isinstance(default, Mapping):
            raise CompilationError(
                message='Must be a mapping',
                path=[_KEY_DEFAULT],
            )
        case_compiler = run_on_key(
            _KEY_DEFAULT,
            self._case_compiler.of_default,
            default,
        )

        case_objs = obj.get(_KEY_CASES, [])
        if not isinstance(case_objs, list):
            raise CompilationError(message='Must be a list', path=[_KEY_CASES])
        cases = map_on_key(
            _KEY_CASES,
            partial(_compile_case, case_compiler),
            case_objs,
        )

        return Scenario(label=label, cases=list(cases))


def _compile_case(case_compiler: CaseCompiler, obj: Any) -> Case:
    if not isinstance(obj, Mapping):
        raise CompilationError(f'Case must be a mapping')
    return case_compiler.compile(obj)
