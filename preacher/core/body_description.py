from typing import Any, List, Optional

from .analysis import Analysis, analyze_json_str
from .description import Description
from .status import merge_statuses
from .verification import Verification


class BodyDescription:

    def __init__(
        self,
        analyze: Analysis = analyze_json_str,
        descriptions: Optional[List[Description]] = None,
    ):
        self._analyze = analyze
        self._descriptions = descriptions or []

    def verify(self, body: str, **kwargs: Any) -> Verification:
        try:
            analyzer = self._analyze(body)
        except Exception as error:
            return Verification.of_error(error)

        verifications = [
            description.verify(analyzer, **kwargs)
            for description in self._descriptions
        ]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status=status, children=verifications)

    @property
    def descriptions(self) -> List[Description]:
        return self._descriptions
