"""Scenario compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Iterator

from preacher.core.case import Case
from .error import CompilationError
from .case import CaseCompiler
from .util import map_on_key


_KEY_SCENARIOS = 'cases'


class Compiler:
    """
    When given an empty object, then generates empty iterator.
    >>> cases = list(Compiler().compile({}))
    >>> cases
    []

    When given not an object, then raises a compilation error.
    >>> next(Compiler().compile({'cases': ''}))
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: cases

    When given a not string case, then raises a compilation error.
    >>> next(Compiler().compile({'cases': ['']}))
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: cases[0]

    Generates an iterator of cases.
    >>> from unittest.mock import MagicMock, patch, sentinel
    >>> case_compiler_mock = MagicMock(
    ...     CaseCompiler,
    ...     compile=MagicMock(return_value=sentinel.case),
    ... )
    >>> with patch(
    ...     f'{__name__}.CaseCompiler',
    ...     return_value=case_compiler_mock
    ... ):
    ...     compiler = Compiler()
    >>> cases = compiler.compile({'cases': [{}]})
    >>> list(cases)
    [sentinel.case]
    >>> list(cases)
    []
    """

    def __init__(self: Compiler) -> None:
        self._case_compiler = CaseCompiler()

    def compile(self: Compiler, obj: Mapping) -> Iterator[Case]:
        case_objs = obj.get(_KEY_SCENARIOS, [])
        if not isinstance(case_objs, list):
            raise CompilationError(
                message='Must be a list',
                path=[_KEY_SCENARIOS],
            )

        return map_on_key(
            _KEY_SCENARIOS,
            self._compile_case,
            case_objs,
        )

    def _compile_case(self: Compiler, obj: Any) -> Case:
        if not isinstance(obj, Mapping):
            raise CompilationError(f'Case must be a mapping')
        return self._case_compiler.compile(obj)
