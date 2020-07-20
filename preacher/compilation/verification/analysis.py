from preacher.compilation.error import CompilationError
from preacher.compilation.util.type import ensure_str
from preacher.core.extraction.analysis import (
    Analysis,
    analyze_json_str,
    analyze_xml_str,
)

_ANALYSIS_MAP = {
    'json': analyze_json_str,
    'xml': analyze_xml_str,
}


class AnalysisCompiler:

    @staticmethod
    def compile(obj: object) -> Analysis:
        """`obj` should be a string."""

        key = ensure_str(obj)
        analysis = _ANALYSIS_MAP.get(key)
        if not analysis:
            raise CompilationError(f'Invalid key: {key}')

        return analysis
