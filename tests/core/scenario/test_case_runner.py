from functools import partial
from typing import Optional
from unittest.mock import Mock, NonCallableMock, sentinel

import requests
from pytest import mark

from preacher.core.context import Context
from preacher.core.extraction import Analyzer
from preacher.core.request import ExecutionReport, Request
from preacher.core.scenario import CaseListener
from preacher.core.scenario.case import Case
from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.status import Status
from preacher.core.unit import UnitRunner
from preacher.core.unit.runner import Result
from preacher.core.verification import Description, ResponseDescription
from preacher.core.verification import ResponseVerification
from preacher.core.verification import Verification

PKG = "preacher.core.scenario.case_runner"


def _retry(func, *_args, **_kwargs):
    return func()


def test_case_listener():
    CaseListener().on_execution(sentinel.execution, sentinel.response)


def test_runner_properties():
    unit_runner = NonCallableMock(UnitRunner, base_url=sentinel.base_url)
    runner = CaseRunner(unit_runner)
    assert runner.base_url is sentinel.base_url


def test_when_disabled():
    case = Case(label=sentinel.label, enabled=False)

    unit_runner = NonCallableMock(UnitRunner)
    runner = CaseRunner(unit_runner=unit_runner)
    actual = runner.run(case)
    assert actual.label is sentinel.label
    assert actual.status is Status.SKIPPED

    unit_runner.run.assert_not_called()


@mark.parametrize(
    ("condition_verifications", "expected_status"),
    (
        (
            [
                Verification(status=Status.SKIPPED),
                Verification(status=Status.UNSTABLE),
                Verification(status=Status.SUCCESS),
            ],
            Status.SKIPPED,
        ),
        (
            [
                Verification(status=Status.SUCCESS),
                Verification(status=Status.FAILURE),
                Verification(status=Status.UNSTABLE),
            ],
            Status.FAILURE,
        ),
    ),
)
def test_given_bad_condition(mocker, condition_verifications, expected_status):
    mocker.patch(f"{PKG}.now", return_value=sentinel.starts)

    def _analyze_context(context: Context) -> Analyzer:
        assert context == Context(foo="bar", starts=sentinel.starts, base_url=sentinel.base_url)
        return sentinel.context_analyzer

    analyze_context = mocker.patch(f"{PKG}.MappingAnalyzer", side_effect=_analyze_context)

    def _verify(
        verification: Verification,
        analyzer: Analyzer,
        context: Optional[Context] = None,
    ) -> Verification:
        assert analyzer is sentinel.context_analyzer
        assert context == Context(foo="bar", starts=sentinel.starts, base_url=sentinel.base_url)
        return verification

    conditions = [
        NonCallableMock(Description, verify=Mock(side_effect=partial(_verify, v)))
        for v in condition_verifications
    ]
    case = Case(
        label=sentinel.label,
        conditions=conditions,
        request=sentinel.request,
        response=sentinel.response,
    )

    unit_runner = NonCallableMock(UnitRunner, base_url=sentinel.base_url)
    listener = NonCallableMock(CaseListener)
    runner = CaseRunner(unit_runner=unit_runner, listener=listener)
    result = runner.run(case, context=Context(foo="bar"))

    assert result.label is sentinel.label
    assert result.status is expected_status

    # Contextual values will disappear.
    for condition in conditions:
        condition.verify.assert_called_once_with(sentinel.context_analyzer, Context(foo="bar"))
    analyze_context.assert_called_once_with(Context(foo="bar"))

    unit_runner.run.assert_not_called()
    listener.on_execution.assert_not_called()


def test_when_given_no_response(mocker):
    mocker.patch(f"{PKG}.now", return_value=sentinel.starts)

    execution = ExecutionReport(status=Status.FAILURE)
    case = Case(label=sentinel.label, request=sentinel.request, response=sentinel.response)

    def _run_unit(
        request: Request,
        requirements: ResponseDescription,
        session: Optional[requests.Session] = None,
        context: Optional[Context] = None,
    ) -> Result:
        assert request is sentinel.request
        assert requirements is sentinel.response
        assert session is None
        assert context == Context(starts=sentinel.starts, base_url=sentinel.base_url)
        return execution, None, None

    unit_runner = NonCallableMock(UnitRunner, base_url=sentinel.base_url)
    unit_runner.run.side_effect = Mock(side_effect=_run_unit)
    listener = NonCallableMock(spec=CaseListener)
    runner = CaseRunner(unit_runner=unit_runner, listener=listener)
    result = runner.run(case)

    assert result.label is sentinel.label
    assert result.status is Status.FAILURE
    assert result.execution is execution
    assert result.response is None

    # Contextual values will disappear.
    unit_runner.run.assert_called_once_with(
        request=sentinel.request,
        requirements=sentinel.response,
        session=None,
        context=Context(),
    )
    listener.on_execution.assert_called_once_with(execution, None)


def test_when_given_an_response(mocker):
    mocker.patch(f"{PKG}.now", return_value=sentinel.starts)

    execution = ExecutionReport(status=Status.SUCCESS, starts=sentinel.starts)
    verification = ResponseVerification(
        response_id=sentinel.response_id,
        status_code=Verification.succeed(),
        headers=Verification.succeed(),
        body=Verification(status=Status.UNSTABLE),
    )

    case = Case(label=sentinel.label, request=sentinel.request, response=sentinel.response)

    def _run_unit(
        request: Request,
        requirements: ResponseDescription,
        session: Optional[requests.Session] = None,
        context: Optional[Context] = None,
    ) -> Result:
        assert request is sentinel.request
        assert requirements is sentinel.response
        assert session is sentinel.session
        assert context == Context(foo="bar", starts=sentinel.starts, base_url=sentinel.base_url)
        return execution, sentinel.response, verification

    unit_runner = NonCallableMock(UnitRunner, base_url=sentinel.base_url)
    unit_runner.run.side_effect = Mock(side_effect=_run_unit)
    listener = NonCallableMock(spec=CaseListener)
    runner = CaseRunner(unit_runner=unit_runner, listener=listener)
    result = runner.run(case, session=sentinel.session, context=Context(foo="bar"))

    assert result.label is sentinel.label
    assert result.status is Status.UNSTABLE
    assert result.execution is execution
    assert result.response is verification

    # Contextual values will disappear.
    unit_runner.run.assert_called_once_with(
        request=sentinel.request,
        requirements=sentinel.response,
        session=sentinel.session,
        context=Context(foo="bar"),
    )
    listener.on_execution.assert_called_once_with(execution, sentinel.response)
