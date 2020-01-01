"""Scenario compilation."""

from collections.abc import Mapping
from typing import List, Optional

from preacher.core.case import Case
from preacher.core.scenario import Scenario
from .case import CaseCompiler
from .description import DescriptionCompiler
from .error import CompilationError, NamedNode, on_key
from .response import ResponseDescriptionCompiler
from .util import map_compile

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

    def compile(self, obj: object) -> Scenario:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        label = obj.get(_KEY_LABEL)
        if label is not None and not isinstance(label, str):
            raise CompilationError(
                message='Must be a string',
                path=[NamedNode(_KEY_LABEL)],
            )

        default_obj = obj.get(_KEY_DEFAULT, {})
        with on_key(_KEY_DEFAULT):
            case_compiler = self._compile_default(default_obj)

        condition_obj = obj.get(_KEY_WHEN, [])
        with on_key(_KEY_WHEN):
            conditions = self._compile_conditions(condition_obj)

        case_obj = obj.get(_KEY_CASES, [])
        with on_key(_KEY_CASES):
            cases = self._compile_cases(case_compiler, case_obj)

        subscenario_obj = obj.get(_KEY_SUBSCENARIOS, [])
        with on_key(_KEY_SUBSCENARIOS):
            subscenarios = self._compile_subscenarios(
                case_compiler,
                subscenario_obj,
            )

        return Scenario(
            label=label,
            conditions=conditions,
            cases=cases,
            subscenarios=subscenarios,
        )

    def _compile_default(self, obj: object) -> CaseCompiler:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError(f'Must be a mapping, given {type(obj)}')
        return self._case_compiler.of_default(obj)

    def _compile_conditions(self, obj: object):
        if not isinstance(obj, list):
            obj = [obj]
        return list(map_compile(self._description_compiler.compile, obj))

    @staticmethod
    def _compile_cases(case_compiler: CaseCompiler, obj: object) -> List[Case]:
        """`obj` should be a list."""

        if not isinstance(obj, list):
            raise CompilationError(f'Must be a list, given {type(obj)}')
        return list(map_compile(case_compiler.compile, obj))

    def _compile_subscenarios(
        self,
        case_compiler: CaseCompiler,
        obj: object,
    ) -> List[Scenario]:
        """`obj` should be a list."""

        if not isinstance(obj, list):
            raise CompilationError(f'Must be a list, given {type(obj)}')
        subscenario_compiler = ScenarioCompiler(
            description_compiler=self._description_compiler,
            case_compiler=case_compiler,
        )
        return list(map_compile(subscenario_compiler.compile, obj))
