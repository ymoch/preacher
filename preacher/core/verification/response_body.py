"""
Response body description.
"""

from typing import List, Optional

from preacher.core.extraction import ResponseBodyAnalyzer
from preacher.core.request import ResponseBody
from preacher.core.value import ValueContext
from .description import Description
from .verification import Verification


class ResponseBodyDescription:

    def __init__(self, descriptions: Optional[List[Description]] = None):
        self._descriptions = descriptions or []

    def verify(self, body: ResponseBody, context: Optional[ValueContext] = None) -> Verification:
        analyzer = ResponseBodyAnalyzer(body)
        return Verification.collect(
            description.verify(analyzer, context)
            for description in self._descriptions
        )
