"""
Tests only that the whole process is run.
Styles should be checked independently.
"""

import os
from dataclasses import dataclass, field
from tempfile import TemporaryDirectory
from typing import Mapping
from unittest.mock import NonCallableMock

from pytest import fixture, mark

from preacher.core.request import (
    ExecutionReport,
    PreparedRequest,
    Response,
    ResponseBody,
)
from preacher.core.scenario import ScenarioResult, CaseResult
from preacher.core.status import Status, StatusedList
from preacher.core.verification import Verification, ResponseVerification
from preacher.presentation.html import HtmlReporter
from . import FILLED_SCENARIO_RESULTS


@dataclass
class ResponseBodyImpl(ResponseBody):
    text: str = ''
    content: bytes = b''


@dataclass
class ResponseImpl(Response):
    elapsed: float = 0.0
    status_code: int = 200
    headers: Mapping[str, str] = field(default_factory=dict)
    body: ResponseBody = field(default=ResponseBodyImpl())

    @property
    def id(self) -> str:
        return 'res-id'


@fixture
def path():
    with TemporaryDirectory() as path:
        yield path


def test_export_execution(path):
    execution = ExecutionReport()

    response_body = NonCallableMock(ResponseBody)
    response_body.text = 'ABC'
    response_body.content = b'ABC'

    response = NonCallableMock(Response)
    response.id = 'res-id'
    response.elapsed = 0.1
    response.status_code = 200
    response.headers = {'key': 'value'}
    response.body = response_body

    reporter = HtmlReporter(path)
    reporter.export_response(execution, response)
    assert os.path.isfile(os.path.join(path, 'responses', 'res-id.html'))


@mark.parametrize('results', [
    [],
    FILLED_SCENARIO_RESULTS,
    [
        ScenarioResult(),
        ScenarioResult(
            label='Scenario 1',
            status=Status.SUCCESS,
            conditions=Verification(
                status=Status.SUCCESS,
                children=[
                    Verification(),
                    Verification(Status.SUCCESS, message='msg'),
                ],
            ),
            cases=StatusedList([
                CaseResult(),
                CaseResult(
                    label='Case 1',
                    execution=ExecutionReport()
                ),
                CaseResult(
                    label='Case 2',
                    conditions=Verification(
                        status=Status.SUCCESS,
                        children=[
                            Verification(),
                            Verification(Status.SUCCESS, message='msg'),
                        ],
                    ),
                    execution=ExecutionReport(
                        status=Status.SUCCESS,
                        request=PreparedRequest(
                            method='GET',
                            url='https://base-url.com/path?foo=bar',
                            headers={'User-Agent': 'Preacher x.x.x'},
                            body='spam=ham',
                        ),
                    ),
                    response=ResponseVerification(
                        response_id='response-id',
                        status=Status.SUCCESS,
                        status_code=Verification(
                            status=Status.SUCCESS,
                            children=[
                                Verification(),
                                Verification(Status.SUCCESS, message='msg'),
                            ],
                        ),
                        headers=Verification(
                            status=Status.SUCCESS,
                            children=[
                                Verification(),
                                Verification(Status.SUCCESS, message='msg'),
                            ],
                        ),
                        body=Verification(
                            status=Status.SUCCESS,
                            children=[
                                Verification(),
                                Verification(Status.SUCCESS, message="msg"),
                            ]
                        )
                    ),
                ),
            ]),
            subscenarios=StatusedList([
                ScenarioResult(),
                ScenarioResult(label='Subscenario 1'),
            ])
        ),
    ]
])
def test_export_results(path, results):
    reporter = HtmlReporter(path)
    reporter.export_results([])
    assert os.path.isfile(os.path.join(path, 'index.html'))
