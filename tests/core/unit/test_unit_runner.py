from unittest.mock import NonCallableMock, sentinel

from pytest import mark, raises

from preacher.core.request import ExecutionReport
from preacher.core.status import Status
from preacher.core.unit.runner import predicate, UnitRunner
from preacher.core.verification import ResponseVerification


@mark.parametrize(('execution', 'verification', 'expected'), [
    (ExecutionReport(Status.UNSTABLE), None, False),
    (ExecutionReport(Status.SUCCESS), None, True),
    (
        ExecutionReport(Status.UNSTABLE),
        NonCallableMock(ResponseVerification, status=Status.SUCCESS),
        False,
    ),
    (
        ExecutionReport(Status.SUCCESS),
        NonCallableMock(ResponseVerification, status=Status.FAILURE),
        False,
    ),
    (
        ExecutionReport(Status.SUCCESS),
        NonCallableMock(ResponseVerification, status=Status.SUCCESS),
        True,
    ),
])
def test_predicate(execution, verification, expected):
    assert predicate((execution, None, verification)) == expected


@mark.parametrize('retry', [-2, -1])
def test_given_invalid_retry_count(retry):
    with raises(ValueError):
        UnitRunner(sentinel.base_url, retry=retry)
