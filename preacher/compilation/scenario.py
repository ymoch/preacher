"""Scenario compilation."""

from __future__ import annotations

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
    """
    When given an empty object, then generates an empty scenario.
    >>> from unittest.mock import MagicMock, call, patch, sentinel
    >>> case_compiler = MagicMock(CaseCompiler)
    >>> compiler = ScenarioCompiler(case_compiler=case_compiler)
    >>> scenario = compiler.compile({})
    >>> scenario.label
    >>> list(scenario.cases())
    []
    >>> case_compiler.of_default.assert_called_once_with({})

    When given not an object, then raises a compilation error.
    >>> ScenarioCompiler().compile({'cases': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: cases

    When given a not string label, then raises a compilation error.
    >>> ScenarioCompiler().compile({'label': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: label

    When given not mapping default, then raises a compilation error.
    >>> ScenarioCompiler().compile({'default': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: default

    When given a not mapping case, then raises a compilation error.
    >>> ScenarioCompiler().compile({'cases': ['']})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: cases[0]

    Generates an iterator of cases.
    >>> default_case_compiler = MagicMock(
    ...     CaseCompiler,
    ...     compile=MagicMock(return_value=sentinel.case),
    ... )
    >>> case_compiler = MagicMock(
    ...     CaseCompiler,
    ...     of_default=MagicMock(return_value=default_case_compiler),
    ... )
    >>> compiler = ScenarioCompiler(case_compiler=case_compiler)
    >>> scenario = compiler.compile({
    ...     'label': 'label',
    ...     'default': {'a': 'b'},
    ...     'cases': [{}, {'k': 'v'}],
    ... })
    >>> scenario.label
    'label'
    >>> list(scenario.cases())
    [sentinel.case, sentinel.case]
    >>> case_compiler.of_default.assert_called_once_with({'a': 'b'})
    >>> default_case_compiler.compile.assert_has_calls([
    ...     call({}),
    ...     call({'k': 'v'})],
    ... )
    """
    def __init__(
        self: ScenarioCompiler,
        case_compiler: Optional[CaseCompiler] = None,
    ) -> None:
        self._case_compiler = case_compiler or CaseCompiler()

    def compile(self: ScenarioCompiler, obj: Mapping) -> Scenario:
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
