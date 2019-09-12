import json
from typing import Any, Callable, Union


class JsonAnalyzer:

    def __init__(self, json_body: Any):
        self._json_body = json_body

    def jq(self, extract: Callable[[Any], Any]) -> Any:
        return extract(self._json_body)


Analyzer = Union[JsonAnalyzer]


def analyze_json_str(value: str) -> Analyzer:
    return JsonAnalyzer(json.loads(value))
