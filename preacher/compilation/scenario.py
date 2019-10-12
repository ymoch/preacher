"""Scenario compilation."""

from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.scenario import Scenario
from .description import DescriptionCompiler
from .error import CompilationError, NamedNode
from .case import CaseCompiler
from .response_description import ResponseDescriptionCompiler
from .util import map_on_key, run_on_key


_KEY_LABEL = 'label'
_KEY_WHEN = 'when'
_KEY_DEFAULT = 'default'
_KEY_CASES = 'cases'
_KEY_SUBSCENARIOS = 'subscenarios'


class ScenarioCompiler:

    def __init__(
        self,
        description_compiler: Optional[DescriptionCompiler] = None,
        case_compiler: Optional[CaseCompiler] = None,
    ):
        self._description_compiler = (
            description_compiler or DescriptionCompiler()
        )
        self._case_compiler = case_compiler or CaseCompiler(
            response_compiler=ResponseDescriptionCompiler(
                description_compiler=self._description_compiler,
            ),
        )

    def compile(self, obj: Any) -> Scenario:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        label = obj.get(_KEY_LABEL)
        if label is not None and not isinstance(label, str):
            raise CompilationError(
                message='Must be a string',
                path=[NamedNode(_KEY_LABEL)],
            )

        default = obj.get(_KEY_DEFAULT, {})
        if not isinstance(default, Mapping):
            raise CompilationError(
                message='Must be a mapping',
                path=[NamedNode(_KEY_DEFAULT)],
            )
        case_compiler = run_on_key(
            _KEY_DEFAULT,
            self._case_compiler.of_default,
            default,
        )

        condition_objs = obj.get(_KEY_WHEN, [])
        if not isinstance(condition_objs, list):
            condition_objs = [condition_objs]
        conditions = list(map_on_key(
            _KEY_WHEN,
            self._description_compiler.compile,
            condition_objs,
        ))

        case_objs = obj.get(_KEY_CASES, [])
        if not isinstance(case_objs, list):
            raise CompilationError(
                message='Must be a list',
                path=[NamedNode(_KEY_CASES)],
            )
        cases = list(map_on_key(_KEY_CASES, case_compiler.compile, case_objs))

        subscenario_objs = obj.get(_KEY_SUBSCENARIOS, [])
        if not isinstance(subscenario_objs, list):
            raise CompilationError(
                message='Must be a list',
                path=[NamedNode(_KEY_SUBSCENARIOS)],
            )
        subscenario_compiler = ScenarioCompiler(case_compiler=case_compiler)
        subscenarios = list(map_on_key(
            _KEY_SUBSCENARIOS,
            subscenario_compiler.compile,
            subscenario_objs,
        ))

        return Scenario(
            label=label,
            conditions=conditions,
            cases=cases,
            subscenarios=subscenarios,
        )
