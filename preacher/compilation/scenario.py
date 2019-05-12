"""Scenario compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from preacher.core.scenario import Scenario
from preacher.core.case import Case
from .error import CompilationError
from .case import CaseCompiler
from .util import map_on_key


_KEY_CASES = 'cases'


class ScenarioCompiler:
    """
    When given an empty object, then generates empty iterator.
    >>> scenario = ScenarioCompiler().compile({})
    >>> scenario.cases
    []

    When given not an object, then raises a compilation error.
    >>> next(ScenarioCompiler().compile({'cases': ''}))
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: cases

    When given a not string case, then raises a compilation error.
    >>> next(ScenarioCompiler().compile({'cases': ['']}))
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: cases[0]

    Generates an iterator of cases.
    >>> from unittest.mock import MagicMock, call, patch, sentinel
    >>> case_compiler = MagicMock(
    ...     CaseCompiler,
    ...     compile=MagicMock(return_value=sentinel.case),
    ... )
    >>> with patch(
    ...     f'{__name__}.CaseCompiler',
    ...     return_value=case_compiler,
    ... ):
    ...     compiler = ScenarioCompiler()
    >>> scenario = compiler.compile({'cases': [{}, {'k': 'v'}]})
    >>> scenario.cases
    [sentinel.case, sentinel.case]
    >>> case_compiler.compile.assert_has_calls([call({}), call({'k': 'v'})])
    """
    def __init__(self: ScenarioCompiler) -> None:
        self._case_compiler = CaseCompiler()

    def compile(self: ScenarioCompiler, obj: Mapping) -> Scenario:
        case_objs = obj.get(_KEY_CASES, [])
        if not isinstance(case_objs, list):
            raise CompilationError(message='Must be a list', path=[_KEY_CASES])
        cases = map_on_key(_KEY_CASES, self._compile_case, case_objs)

        return Scenario(cases=list(cases))

    def _compile_case(self: ScenarioCompiler, obj: Any) -> Case:
        if not isinstance(obj, Mapping):
            raise CompilationError(f'Case must be a mapping')
        return self._case_compiler.compile(obj)
