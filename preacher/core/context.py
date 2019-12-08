from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

from .analysis import Analyzer, JsonAnalyzer
from .datetime import now


@dataclass(frozen=True)
class ApplicationContextComponent:
    starts: datetime = field(default_factory=now)
    base_url: str = ''
    retry: int = 0
    delay: float = 0.1
    timeout: Optional[float] = None


@dataclass(frozen=True)
class ApplicationContext:
    app: ApplicationContextComponent = field(
        default_factory=ApplicationContextComponent
    )


@dataclass(frozen=True)
class ScenarioContextComponent:
    starts: datetime = field(default_factory=now)


@dataclass(frozen=True)
class ScenarioContext(ApplicationContext):
    scenario: ScenarioContextComponent = field(
        default_factory=ScenarioContextComponent
    )


@dataclass(frozen=True)
class CaseContextComponent:
    started: datetime = field(default_factory=now)


@dataclass(frozen=True)
class CaseContext(ScenarioContext):
    case: CaseContextComponent = field(default_factory=CaseContextComponent)


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
