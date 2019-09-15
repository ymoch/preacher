from typing import Any, Callable

from preacher.core.analysis import Analyzer, analyze_json_str, analyze_xml_str
from .error import CompilationError


_ANALYSIS_MAP = {
    'json': analyze_json_str,
    'xml': analyze_xml_str,
}


class AnalysisCompiler:

    def compile(self, obj: Any) -> Callable[[str], Analyzer]:
        """`obj` should be a string."""
        if not isinstance(obj, str):
            raise CompilationError('Must be a string')

        analysis = _ANALYSIS_MAP.get(obj)
        if not analysis:
            raise CompilationError(f'Invalid key: {obj}')

        return analysis
