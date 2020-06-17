from dataclasses import asdict
from datetime import datetime

from .analysis import Analyzer, JsonAnalyzer


def _to_serializable(value: object) -> object:
    if isinstance(value, dict):
        return {k: _to_serializable(v) for (k, v) in value.items()}
    if isinstance(value, list):
        return [_to_serializable(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def analyze_context(context) -> Analyzer:
    return JsonAnalyzer(_to_serializable(asdict(context)))
