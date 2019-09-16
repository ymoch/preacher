from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.body_description import BodyDescription
from .analysis import AnalysisCompiler
from .description import DescriptionCompiler
from .error import CompilationError
from .util import map_on_key, run_on_key


_KEY_ANALYSIS = 'analyze_as'
_KEY_DESCRIPTIONS = 'descriptions'

_DEFAULT_ANALYSIS = 'json'


class BodyDescriptionCompiler:

    def __init__(
        self,
        analysis_compiler: Optional[AnalysisCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._analysis_compiler = analysis_compiler or AnalysisCompiler()
        self._description_compiler = (
            description_compiler or DescriptionCompiler()
        )

    def compile(self, obj: Any) -> BodyDescription:
        """
        `obj` should be a mapping or a list.
        An empty list results in an empty description.
        """

        if isinstance(obj, list):
            return self.compile({_KEY_DESCRIPTIONS: obj})
        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping or a list')

        analyze = run_on_key(
            _KEY_ANALYSIS,
            self._analysis_compiler.compile,
            obj.get(_KEY_ANALYSIS, _DEFAULT_ANALYSIS),
        )

        desc_objs = obj.get(_KEY_DESCRIPTIONS)
        if desc_objs is None:
            # Compile as a description to be compatible.
            description = self._description_compiler.compile(obj)
            return BodyDescription(
                descriptions=[description],
                analyze=analyze,
            )

        if not isinstance(desc_objs, list):
            desc_objs = [desc_objs]

        descriptions = list(map_on_key(
            _KEY_DESCRIPTIONS,
            self._description_compiler.compile,
            desc_objs,
        ))
        return BodyDescription(descriptions=descriptions, analyze=analyze)
