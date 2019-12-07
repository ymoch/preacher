from dataclasses import asdict, dataclass
from datetime import datetime

from .analysis import Analyzer, JsonAnalyzer


@dataclass(frozen=True)
class ApplicationContextComponent:
    started: datetime
    base_url: str


@dataclass(frozen=True)
class ApplicationContext:
    app: ApplicationContextComponent


@dataclass(frozen=True)
class ScenarioContextComponent:
    started: datetime


@dataclass(frozen=True)
class ScenarioContext(ApplicationContext):
    scenario: ScenarioContextComponent


@dataclass(frozen=True)
class CaseContext:
    started: datetime


@dataclass(frozen=True)
class CaseContext(ScenarioContext):
    case: CaseContext


@dataclass(frozen=True)
class Context:
    """Deprecated!"""
    base_url: str = ''

    def analyze(self) -> Analyzer:
        return JsonAnalyzer(asdict(self))
