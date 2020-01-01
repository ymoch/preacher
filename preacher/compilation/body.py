from __future__ import annotations

from collections.abc import Mapping
from typing import List, Optional

from preacher.core.body import BodyDescription
from preacher.core.description import Description
from .analysis import AnalysisCompiler
from .description import DescriptionCompiler
from .error import CompilationError, on_key
from .util import map_compile

_KEY_ANALYSIS = 'analyze_as'
_KEY_DESCRIPTIONS = 'descriptions'


class BodyDescriptionCompiler:

    def __init__(
        self,
        analysis: AnalysisCompiler,
        description: DescriptionCompiler,
        default: Optional[BodyDescription] = None,
    ):
        self._analysis = analysis
        self._description = description
        self._default = default or BodyDescription()

    def of_default(self, default: BodyDescription) -> BodyDescriptionCompiler:
        return BodyDescriptionCompiler(
            analysis=self._analysis,
            description=self._description,
            default=default,
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

        analyze = self._default.analyze
        analyze_obj = obj.get(_KEY_ANALYSIS)
        if analyze_obj is not None:
            with on_key(_KEY_ANALYSIS):
                analyze = self._analysis.compile(analyze_obj)

        descriptions = self._default.descriptions
        descriptions_obj = obj.get(_KEY_DESCRIPTIONS)
        if descriptions_obj is not None:
            descriptions = self._compile_descriptions(descriptions_obj)

        return BodyDescription(analyze=analyze, descriptions=descriptions)

    def _compile_descriptions(self, obj: object) -> List[Description]:
        if not isinstance(obj, list):
            obj = [obj]

        with on_key(_KEY_DESCRIPTIONS):
            return list(map_compile(self._description.compile, obj))
