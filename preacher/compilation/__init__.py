"""Compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Iterator

from preacher.core.scenario import Scenario
from .error import CompilationError
from .scenario import ScenarioCompiler
from .util import map_on_key


_KEY_SCENARIOS = 'scenarios'


class Compiler:
    """
    When given an empty object, then generates empty iterator.
    >>> scenarios = list(Compiler().compile({}))
    >>> scenarios
    []

    When given not an object, then raises a compilation error.
    >>> next(Compiler().compile({'scenarios': ''}))
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: scenarios

    When given a not string scenario, then raises a compilation error.
    >>> next(Compiler().compile({'scenarios': ['']}))
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: scenarios[0]

    Generates an iterator of scenarios.
    >>> from unittest.mock import MagicMock, patch, sentinel
    >>> scenario_compiler_mock = MagicMock(
    ...     ScenarioCompiler,
    ...     compile=MagicMock(return_value=sentinel.scenario),
    ... )
    >>> with patch(
    ...     f'{__name__}.ScenarioCompiler',
    ...     return_value=scenario_compiler_mock
    ... ):
    ...     compiler = Compiler()
    >>> scenarios = compiler.compile({'scenarios': [{}]})
    >>> list(scenarios)
    [sentinel.scenario]
    >>> list(scenarios)
    []
    """

    def __init__(self: Compiler) -> None:
        self._scenario_compiler = ScenarioCompiler()

    def compile(self: Compiler, obj: Mapping) -> Iterator[Scenario]:
        scenario_objs = obj.get(_KEY_SCENARIOS, [])
        if not isinstance(scenario_objs, list):
            raise CompilationError(
                message='Must be a list',
                path=[_KEY_SCENARIOS],
            )

        return map_on_key(
            _KEY_SCENARIOS,
            self._compile_scenario,
            scenario_objs,
        )

    def _compile_scenario(self: Compiler, obj: Any) -> Scenario:
        if not isinstance(obj, Mapping):
            raise CompilationError(f'Scenario must be a mapping')
        return self._scenario_compiler.compile(obj)
