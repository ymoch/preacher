from unittest.mock import Mock, NonCallableMock, sentinel

from preacher.core.status import Status
from preacher.core.verification.description import Description
from preacher.core.verification.response_body import ResponseBodyDescription
from preacher.core.verification.verification import Verification

PKG = 'preacher.core.verification.response_body'


def test_given_descriptions(mocker):
    analyze = mocker.patch(f'{PKG}.ResponseBodyAnalyzer', return_value=sentinel.analyzer)

    descriptions = [
        NonCallableMock(Description, verify=Mock(
            return_value=Verification(status=Status.UNSTABLE)
        )),
        NonCallableMock(Description, verify=Mock(
            return_value=Verification.succeed()
        )),
    ]
    description = ResponseBodyDescription(descriptions)
    verification = description.verify(sentinel.body, sentinel.context)
    assert verification.status == Status.UNSTABLE
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.SUCCESS

    analyze.assert_called_once_with(sentinel.body)
    for description in descriptions:
        description.verify.assert_called_once_with(sentinel.analyzer, sentinel.context)
