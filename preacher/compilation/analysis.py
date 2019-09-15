from typing import Any

from preacher.core.analysis import Analysis, analyze_json_str, analyze_xml_str
from .error import CompilationError


_ANALYSIS_MAP = {
    'json': analyze_json_str,
    'xml': analyze_xml_str,
}


class AnalysisCompiler:

    def compile(self, obj: Any) -> Analysis:
        """`obj` should be a string."""
        if not isinstance(obj, str):
            raise CompilationError('Must be a string')

        analysis = _ANALYSIS_MAP.get(obj)
        if not analysis:
            raise CompilationError(f'Invalid key: {obj}')

        return analysis
