from typing import Any, Callable, List

from .analysis import Analysis, analyze_json_str
from .description import Description
from .status import merge_statuses
from .verification import Verification


class BodyDescription:

    def __init__(
        self,
        descriptions: List[Description] = [],
        analyze: Analysis = analyze_json_str,
    ):
        self._descriptions = descriptions
        self._analyze = analyze

    def verify(self, body: str, **kwargs: Any) -> Verification:
        try:
            analyzer = self._analyze(body)
        except Exception as error:
            return Verification.of_error(error)

        verifications = [
            describe(analyzer, **kwargs)
            for describe in self._descriptions
        ]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status=status, children=verifications)

    @property
    def descriptions(self) -> List[Description]:
        return self._descriptions
