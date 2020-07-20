from typing import List

from preacher.core.request import ExecutionReport, PreparedRequest
from preacher.core.scenario import ScenarioResult, CaseResult
from preacher.core.status import Status, StatusedList
from preacher.core.verification import Verification, ResponseVerification

FILLED_SCENARIO_RESULTS: List[ScenarioResult] = [
    ScenarioResult(),
    ScenarioResult(
        label='Scenario 1',
        status=Status.SUCCESS,
        message='msg',
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
                    message='msg',
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
