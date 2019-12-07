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
class CaseContextComponent:
    started: datetime


@dataclass(frozen=True)
class CaseContext(ScenarioContext):
    case: CaseContextComponent


@dataclass(frozen=True)
class Context:
    """Deprecated!"""
    base_url: str = ''


def analyze_context(context) -> Analyzer:
    return JsonAnalyzer(asdict(context))