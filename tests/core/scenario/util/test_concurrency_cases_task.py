from pytest import raises

from preacher.core.scenario.case import CaseResult
from preacher.core.scenario.status import StatusedList
from preacher.core.scenario.util.concurrency import CasesTask


def test_incomplete_implementation():
    class _IncompleteCasesTask(CasesTask):

        def result(self) -> StatusedList[CaseResult]:
            return super().result()

    task = _IncompleteCasesTask()
    with raises(NotImplementedError):
        task.result()
