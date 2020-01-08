from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

from preacher.core.datetime import now
from .analysis import Analyzer, JsonAnalyzer


@dataclass(frozen=True)
class ScenarioContext:
    starts: datetime = field(default_factory=now)
    base_url: str = ''
    retry: int = 0
    delay: float = 0.1
    timeout: Optional[float] = None


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
