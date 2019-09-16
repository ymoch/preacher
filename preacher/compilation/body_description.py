from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
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
class BodyDescriptionCompiled:
    analyze: Optional[Analysis] = None
    descriptions: Optional[List[Description]] = None

    def replace(
        self,
        replacer: BodyDescriptionCompiled
    ) -> BodyDescriptionCompiled:
        replacements = {k: v for (k, v) in asdict(replacer) if v is not None}
        return replace(self, **replacements)

    def convert(self) -> BodyDescription:
        return BodyDescription(
            analyze=or_default(self.analyze, analyze_json_str),
            descriptions=or_default(self.descriptions, []),
        )


class BodyDescriptionCompiler:

    def __init__(
        self,
        default: BodyDescriptionCompiled = None,
        analysis_compiler: Optional[AnalysisCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._default = default or BodyDescriptionCompiled()
        self._analysis_compiler = analysis_compiler or AnalysisCompiler()
        self._description_compiler = (
            description_compiler or DescriptionCompiler()
        )

    def compile(self, obj: Any) -> BodyDescriptionCompiled:
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

        replacements['descriptions'] = (  # type: ignore
            self._compile_descriptions(obj)
        )

        return replace(self._default, **replacements)

    def _compile_descriptions(self, obj: Any) -> List[Description]:
        desc_objs = obj.get(_KEY_DESCRIPTIONS)
        if desc_objs is None:
            # Compile as a description to be compatible.
            return [self._description_compiler.compile(obj)]

        if not isinstance(desc_objs, list):
            desc_objs = [desc_objs]

        return list(map_on_key(
            _KEY_DESCRIPTIONS,
            self._description_compiler.compile,
            desc_objs,
        ))
