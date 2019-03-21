"""Compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Iterator

from preacher.core.scenario import Scenario
from .error import CompilationError
from .scenario import compile_scenario


def compile(obj: Mapping) -> Iterator[Scenario]:
    """
    >>> scenarios = list(compile({}))
    >>> scenarios
    []

    >>> scenarios = compile({'scenarios': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: scenarios ...

    >>> from unittest.mock import sentinel, patch
    >>> scenario_patch = patch(
    ...     f'{__name__}.compile_scenario',
    ...     return_value=sentinel.scenario,
    ... )
    >>> scenarios = compile({'scenarios': [{}, '']})
    >>> with scenario_patch as scenario_mock:
    ...     next(scenarios)
    ...     scenario_mock.call_args
    sentinel.scenario
    call({})
    >>> with scenario_patch as scenario_mock:
    ...     next(scenarios)
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario ...
    """
    scenario_objs = obj.get('scenarios', [])
    if not isinstance(scenario_objs, list):
        raise CompilationError(f'scenarios must be a list: {scenario_objs}')
    return map(_compile_scenario, scenario_objs)


def _compile_scenario(obj: Any) -> Scenario:
    if not isinstance(obj, Mapping):
        raise CompilationError(f'Scenario must be a mapping: {obj}')
    return compile_scenario(obj)
