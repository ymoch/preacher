from __future__ import annotations

from preacher.core.case import Case
from preacher.presentation.logging import LoggingPresentation


class Application:
    def __init__(
        self: Application,
        base_url: str,
        view: LoggingPresentation,
    ) -> None:
        self._view = view
        self._base_url = base_url
        self._is_succeeded = True

    @property
    def is_succeeded(self: Application) -> bool:
        return self._is_succeeded

    def consume_case(self: Application, case: Case) -> None:
        result = case(base_url=self._base_url)

        self._is_succeeded &= result.status.is_succeeded
        self._view.show_case_result(result, 'Response')
