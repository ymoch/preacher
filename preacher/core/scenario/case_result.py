from dataclasses import dataclass, field
from typing import Optional

from preacher.core.request import ExecutionReport
from preacher.core.status import Statused, Status, merge_statuses
from preacher.core.verification import Verification, ResponseVerification


@dataclass(frozen=True)
class CaseResult(Statused):
    """
    Results for the test cases.
    """

    label: Optional[str] = None
    conditions: Verification = field(default_factory=Verification)
    execution: ExecutionReport = field(default_factory=ExecutionReport)
    response: Optional[ResponseVerification] = None

    @property
    def status(self) -> Status:  # HACK: should be cached
        if self.conditions.status == Status.UNSTABLE:
            return Status.SKIPPED
        if self.conditions.status == Status.FAILURE:
            return Status.FAILURE

        return merge_statuses(
            [
                self.execution.status,
                self.response.status if self.response else Status.SKIPPED,
            ]
        )
