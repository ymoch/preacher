import os
from tempfile import TemporaryDirectory

from pytest import fixture, mark

from preacher.core.request import ExecutionReport, PreparedRequest
from preacher.core.scenario import ScenarioResult, CaseResult
from preacher.core.status import Status, StatusedList
from preacher.core.verification import Verification, ResponseVerification
from preacher.presentation.html import HtmlReporter


@fixture
def path():
    with TemporaryDirectory() as path:
        yield path


@mark.parametrize('results', [
    [],
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
def test_reporting(path, results):
    reporter = HtmlReporter(path)
    reporter.export_results([])

    assert os.path.isfile(os.path.join(path, 'index.html'))
