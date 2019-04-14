"""Compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Iterator

from preacher.core.scenario import Scenario
from .error import CompilationError
from .scenario import compile_scenario
from .util import map_on_key


_KEY_SCENARIOS = 'scenarios'


def compile(obj: Mapping) -> Iterator[Scenario]:
    """
    >>> scenarios = list(compile({}))
    >>> scenarios
    []

    >>> next(compile({'scenarios': ''}))
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: scenarios

    >>> from unittest.mock import sentinel, patch
    >>> scenario_patch = patch(
    ...     f'{__name__}.compile_scenario',
    ...     return_value=sentinel.scenario,
    ... )
    >>> scenarios = compile({'scenarios': [{}, '']})
    >>> with scenario_patch as scenario_mock:
    ...     next(scenarios)
    ...     scenario_mock.assert_called_once_with({})
    sentinel.scenario
    >>> with scenario_patch as scenario_mock:
    ...     next(scenarios)
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: scenarios[1]
    """
    scenario_objs = obj.get(_KEY_SCENARIOS, [])
    if not isinstance(scenario_objs, list):
        raise CompilationError(message='Must be a list', path=[_KEY_SCENARIOS])

    return map_on_key(_KEY_SCENARIOS, _compile_scenario, scenario_objs)


def _compile_scenario(obj: Any) -> Scenario:
    if not isinstance(obj, Mapping):
        raise CompilationError(f'Scenario must be a mapping')
    return compile_scenario(obj)
