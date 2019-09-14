from collections.abc import Mapping
from typing import Any, Callable, Optional

from preacher.core.analysis import Analyzer, analyze_json_str, analyze_xml_str
from preacher.core.body_description import BodyDescription
from .description import DescriptionCompiler
from .error import CompilationError
from .util import map_on_key, run_on_key


_KEY_ANALYSIS = 'analyze_as'
_KEY_DESCRIPTIONS = 'descriptions'

_ANALYSIS_MAP = {
    'json': analyze_json_str,
    'xml': analyze_xml_str,
}


class BodyDescriptionCompiler:

    def __init__(
        self,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
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

        analyze = run_on_key(_KEY_ANALYSIS, self._compile_analysis, obj)

        desc_objs = obj.get(_KEY_DESCRIPTIONS)
        if desc_objs is None:
            # Compile as a description to be compatible.
            description = self._description_compiler.compile(obj)
            return BodyDescription(descriptions=[description])

        if not isinstance(desc_objs, list):
            desc_objs = [desc_objs]

        descriptions = list(map_on_key(
            _KEY_DESCRIPTIONS,
            self._description_compiler.compile,
            desc_objs,
        ))
        return BodyDescription(descriptions=descriptions, analyze=analyze)

    def _compile_analysis(self, obj: Mapping) -> Callable[[str], Analyzer]:
        analysis_key = obj.get(_KEY_ANALYSIS, 'json')
        if not isinstance(analysis_key, str):
            raise CompilationError('Must be a string')

        analysis = _ANALYSIS_MAP.get(analysis_key)
        if not analysis:
            raise CompilationError(f'Invalid key: {analysis_key}')

        return analysis
