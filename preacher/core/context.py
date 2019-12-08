from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

from .analysis import Analyzer, JsonAnalyzer
from .datetime import now


@dataclass(frozen=True)
class ApplicationContextComponent:
    started: datetime = field(default_factory=now)
    base_url: str = ''
    retry: int = 0
    delay: float = 0.1
    timeout: Optional[float] = None


@dataclass(frozen=True)
class ApplicationContext:
    app: ApplicationContextComponent


@dataclass(frozen=True)
class ScenarioContextComponent:
    started: datetime = field(default_factory=now)


@dataclass(frozen=True)
class ScenarioContext(ApplicationContext):
    scenario: ScenarioContextComponent


@dataclass(frozen=True)
class CaseContextComponent:
    started: datetime = field(default_factory=now)


@dataclass(frozen=True)
class CaseContext(ScenarioContext):
    case: CaseContextComponent


def analyze_context(context) -> Analyzer:
    return JsonAnalyzer(asdict(context))
