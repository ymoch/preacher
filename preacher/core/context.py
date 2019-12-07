from dataclasses import asdict, dataclass
from datetime import datetime

from .analysis import Analyzer, JsonAnalyzer


@dataclass(frozen=True)
class ApplicationContext:
    started: datetime
    base_url: str


@dataclass(frozen=True)
class ScenarioContext:
    started: datetime


@dataclass(frozen=True)
class CaseContext:
    started: datetime


@dataclass(frozen=True)
class Context:
    base_url: str = ''

    def analyze(self) -> Analyzer:
        return JsonAnalyzer(asdict(self))
