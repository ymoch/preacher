from typing import Optional

from preacher.core.request import ExecutionReport, Response


class CaseListener:
    """
    Interface to listen to running cases.
    Default implementations do nothing.
    """

    def on_execution(self, execution: ExecutionReport, response: Optional[Response]) -> None:
        pass
