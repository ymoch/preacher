from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import List, Optional

from preacher.core.scenario.analysis import Analysis, analyze_json_str
from preacher.core.scenario.body import BodyDescription
from preacher.core.scenario.description import Description
from .analysis import AnalysisCompiler
from .description import DescriptionCompiler
from .error import CompilationError, on_key
from .util import map_compile, or_else

_KEY_ANALYSIS = 'analyze_as'
_KEY_DESCRIPTIONS = 'descriptions'


@dataclass(frozen=True)
class BodyDescriptionCompiled:
    analyze: Optional[Analysis] = None
    descriptions: Optional[List[Description]] = None

    def replace(
        self,
        other: BodyDescriptionCompiled,
    ) -> BodyDescriptionCompiled:
        return BodyDescriptionCompiled(
            analyze=or_else(other.analyze, self.analyze),
            descriptions=or_else(other.descriptions, self.descriptions),
        )

    def fix(self) -> BodyDescription:
        return BodyDescription(
            analyze=self.analyze or analyze_json_str,
            descriptions=self.descriptions,
        )


class BodyDescriptionCompiler:

    def __init__(
        self,
        analysis: AnalysisCompiler,
        description: DescriptionCompiler,
        default: Optional[BodyDescriptionCompiled] = None,
    ):
        self._analysis = analysis
        self._description = description
        self._default = default or BodyDescriptionCompiled()

    def compile(self, obj: object) -> BodyDescriptionCompiled:
        """
        `obj` should be a mapping or a list.
        An empty list results in an empty description.
        """

        if isinstance(obj, list):
            return self.compile({_KEY_DESCRIPTIONS: obj})
        if not isinstance(obj, Mapping):
            message = f'Must be a map or a list, given {type(obj)}'
            raise CompilationError(message)

        compiled = self._default

        analyze_obj = obj.get(_KEY_ANALYSIS)
        if analyze_obj is not None:
            with on_key(_KEY_ANALYSIS):
                analyze = self._analysis.compile(analyze_obj)
            compiled = replace(compiled, analyze=analyze)

        descriptions_obj = obj.get(_KEY_DESCRIPTIONS)
        if descriptions_obj is not None:
            descriptions = self._compile_descriptions(descriptions_obj)
            compiled = replace(compiled, descriptions=descriptions)

        return compiled

    def of_default(
        self,
        default: BodyDescriptionCompiled
    ) -> BodyDescriptionCompiler:
        return BodyDescriptionCompiler(
            analysis=self._analysis,
            description=self._description,
            default=self._default.replace(default),
        )

    def _compile_descriptions(self, obj: object) -> List[Description]:
        if not isinstance(obj, list):
            obj = [obj]

        with on_key(_KEY_DESCRIPTIONS):
            return list(map_compile(self._description.compile, obj))
