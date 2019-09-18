from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any, List, Optional

from preacher.core.analysis import Analysis, analyze_json_str
from preacher.core.body_description import BodyDescription
from preacher.core.description import Description
from .analysis import AnalysisCompiler
from .description import DescriptionCompiler
from .error import CompilationError
from .util import map_on_key, or_default, run_on_key


_KEY_ANALYSIS = 'analyze_as'
_KEY_DESCRIPTIONS = 'descriptions'


@dataclass(frozen=True)
class Compiled:
    analyze: Optional[Analysis] = None
    descriptions: Optional[List[Description]] = None

    def convert(self) -> BodyDescription:
        return BodyDescription(
            analyze=or_default(self.analyze, analyze_json_str),
            descriptions=or_default(self.descriptions, []),
        )


class BodyDescriptionCompiler:

    def __init__(
        self,
        default: Optional[Compiled] = None,
        analysis_compiler: Optional[AnalysisCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._default = default or Compiled()
        self._analysis_compiler = analysis_compiler or AnalysisCompiler()
        self._description_compiler = (
            description_compiler or DescriptionCompiler()
        )

    def of_default(
        self,
        default: Optional[Compiled],
    ) -> BodyDescriptionCompiler:
        return BodyDescriptionCompiler(
            default=default,
            analysis_compiler=self._analysis_compiler,
            description_compiler=self._description_compiler,
        )

    def compile(self, obj: Any) -> Compiled:
        """
        `obj` should be a mapping or a list.
        An empty list results in an empty description.
        """

        if isinstance(obj, list):
            return self.compile({_KEY_DESCRIPTIONS: obj})
        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping or a list')

        replacements = {}

        analyze_obj = obj.get(_KEY_ANALYSIS)
        if analyze_obj is not None:
            replacements['analyze'] = run_on_key(
                _KEY_ANALYSIS,
                self._analysis_compiler.compile,
                analyze_obj,
            )

        descs_obj = obj.get(_KEY_DESCRIPTIONS)
        if descs_obj is not None:
            replacements['descriptions'] = (  # type: ignore
                self._compile_descriptions(descs_obj)
            )

        return replace(self._default, **replacements)

    def _compile_descriptions(self, obj: Any) -> List[Description]:
        if not isinstance(obj, list):
            obj = [obj]

        return list(map_on_key(
            _KEY_DESCRIPTIONS,
            self._description_compiler.compile,
            obj,
        ))
