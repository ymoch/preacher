"""
Response body description.
"""

from typing import List, Optional

from preacher.core.response import ResponseBody
from .analysis import Analysis, analyze_json_str
from .analysis_description import AnalysisDescription
from .verification import Verification, collect


class BodyDescription:

    def __init__(
        self,
        analyze: Analysis = analyze_json_str,
        descriptions: Optional[List[AnalysisDescription]] = None,
    ):
        self._analyze = analyze
        self._descriptions = descriptions or []

    def verify(self, body: ResponseBody, **kwargs) -> Verification:
        try:
            analyzer = self._analyze(body)
        except Exception as error:
            return Verification.of_error(error)

        return collect(
            description.verify(analyzer, **kwargs)
            for description in self._descriptions
        )
