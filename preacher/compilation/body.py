from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import List, Optional

from preacher.core.analysis import Analysis, analyze_json_str
from preacher.core.body import BodyDescription
from preacher.core.description import Description
from .analysis import AnalysisCompiler
from .description import DescriptionCompiler
from .error import CompilationError, on_key
from .util import map_compile, or_default

_KEY_ANALYSIS = 'analyze_as'
_KEY_DESCRIPTIONS = 'descriptions'


@dataclass(frozen=True)
class _Compiled:
    analyze: Optional[Analysis] = None
    descriptions: Optional[List[Description]] = None

    def convert(self) -> BodyDescription:
        return BodyDescription(
            analyze=or_default(self.analyze, analyze_json_str),
            descriptions=self.descriptions,
        )


class BodyDescriptionCompiler:

    def __init__(
        self,
        analysis: AnalysisCompiler,
        description: DescriptionCompiler,
        default_analyze: Optional[Analysis] = None,
        default_descriptions: Optional[List[Description]] = None,
    ):
        self._analysis = analysis
        self._description = description
        self._default_analyze = default_analyze or analyze_json_str
        self._default_descriptions = default_descriptions or []

    def of_default(self, default: BodyDescription) -> BodyDescriptionCompiler:
        return BodyDescriptionCompiler(
            analysis=self._analysis,
            description=self._description,
            default_analyze=default.analyze,
            default_descriptions=default.descriptions,
        )

    def compile(self, obj: object) -> BodyDescription:
        """
        `obj` should be a mapping or a list.
        An empty list results in an empty description.
        """

        if isinstance(obj, list):
            return self.compile({_KEY_DESCRIPTIONS: obj})
        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping or a list')

        analyze = self._default_analyze
        analyze_obj = obj.get(_KEY_ANALYSIS)
        if analyze_obj is not None:
            with on_key(_KEY_ANALYSIS):
                analyze = self._analysis.compile(analyze_obj)

        descriptions = self._default_descriptions
        descriptions_obj = obj.get(_KEY_DESCRIPTIONS)
        if descriptions_obj is not None:
            descriptions = self._compile_descriptions(descriptions_obj)

        return BodyDescription(analyze=analyze, descriptions=descriptions)

    def _compile_descriptions(self, obj: object) -> List[Description]:
        if not isinstance(obj, list):
            obj = [obj]

        with on_key(_KEY_DESCRIPTIONS):
            return list(map_compile(self._description.compile, obj))
