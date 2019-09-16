from collections.abc import Mapping
from typing import Any, List, Optional

from preacher.core.body_description import BodyDescription
from preacher.core.description import Description
from .analysis import AnalysisCompiler
from .description import DescriptionCompiler
from .error import CompilationError
from .util import map_on_key, run_on_key


_KEY_ANALYSIS = 'analyze_as'
_KEY_DESCRIPTIONS = 'descriptions'


class BodyDescriptionCompiler:

    def __init__(
        self,
        default: BodyDescription = None,
        analysis_compiler: Optional[AnalysisCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._default = default or BodyDescription()
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

        analyze = None
        analyze_obj = obj.get(_KEY_ANALYSIS)
        if analyze_obj is not None:
            analyze = run_on_key(
                _KEY_ANALYSIS,
                self._analysis_compiler.compile,
                analyze_obj,
            )

        descriptions = self._compile_descriptions(obj)

        return self._default.replace(
            analyze=analyze,
            descriptions=descriptions,
        )

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
