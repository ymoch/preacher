"""Scenario compilation."""

from collections.abc import Mapping
from typing import List, Optional

from preacher.core.case import Case
from preacher.core.scenario import Scenario
from .argument import Arguments, inject_arguments
from .case import CaseCompiler
from .description import DescriptionCompiler
from .error import CompilationError, on_key
from .util import map_compile, compile_optional_str

_KEY_LABEL = 'label'
_KEY_WHEN = 'when'
_KEY_DEFAULT = 'default'
_KEY_CASES = 'cases'
_KEY_SUBSCENARIOS = 'subscenarios'


class ScenarioCompiler:

    def __init__(self, description: DescriptionCompiler, case: CaseCompiler):
        self._description = description
        self._case = case

    def compile(
        self,
        obj: object,
        arguments: Optional[Arguments] = None,
    ) -> Scenario:
        """
        Compile the given object into a scenario.

        Args:
            obj: A compiled object, which should be a mapping.
            arguments: Arguments to inject.
        Returns:
            The scenario as the result of compilation.
        Raises:
            CompilationError: when the compilation fails.
        """

        arguments = arguments or {}
        obj = inject_arguments(obj, arguments)

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        label_obj = obj.get(_KEY_LABEL)
        with on_key(_KEY_LABEL):
            label = compile_optional_str(label_obj)

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
        return self._case.of_default(obj)

    def _compile_conditions(self, obj: object):
        if not isinstance(obj, list):
            obj = [obj]
        return list(map_compile(self._description.compile, obj))

    @staticmethod
    def _compile_cases(case_compiler: CaseCompiler, obj: object) -> List[Case]:
        """`obj` should be a list."""

        if not isinstance(obj, list):
            raise CompilationError(f'Must be a list, given {type(obj)}')
        return list(map_compile(case_compiler.compile, obj))

    def _compile_subscenarios(
        self,
        case: CaseCompiler,
        obj: object,
    ) -> List[Scenario]:
        """`obj` should be a list."""

        if not isinstance(obj, list):
            raise CompilationError(f'Must be a list, given {type(obj)}')
        compiler = ScenarioCompiler(description=self._description, case=case)
        return list(map_compile(compiler.compile, obj))
