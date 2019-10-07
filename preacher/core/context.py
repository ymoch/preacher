from dataclasses import asdict, dataclass

from .analysis import Analyzer, JsonAnalyzer


@dataclass
class Context:
    base_url: str = ''

    def analyze(self) -> Analyzer:
        return JsonAnalyzer(asdict(self))
