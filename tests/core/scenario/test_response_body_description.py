from unittest.mock import Mock, NonCallableMock, sentinel

from preacher.core.scenario.description import Description
from preacher.core.scenario.response_body import ResponseBodyDescription
from preacher.core.scenario.verification import Verification
from preacher.core.status import Status


def test_given_invalid_body():
    descriptions = [
        NonCallableMock(Description, verify=Mock(
            return_value=Verification.succeed()
        )),
    ]
    analyze = Mock(side_effect=RuntimeError('parse error'))

    description = ResponseBodyDescription(
        descriptions=descriptions,
        analyze=analyze,
    )
    verification = description.verify(sentinel.body)
    assert verification.status == Status.FAILURE
    assert verification.message.endswith('parse error')

    analyze.assert_called_once_with(sentinel.body)
    descriptions[0].verify.assert_not_called()


def test_given_descriptions():
    descriptions = [
        NonCallableMock(Description, verify=Mock(
            return_value=Verification(status=Status.UNSTABLE)
        )),
        NonCallableMock(Description, verify=Mock(
            return_value=Verification.succeed()
        )),
    ]
    analyze = Mock(return_value=sentinel.body)
    description = ResponseBodyDescription(
        descriptions=descriptions,
        analyze=analyze,
    )
    verification = description.verify(sentinel.body, sentinel.context)
    assert verification.status == Status.UNSTABLE
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.SUCCESS

    analyze.assert_called_once_with(sentinel.body)
    for description in descriptions:
        description.verify.assert_called_once_with(
            sentinel.body,
            sentinel.context,
        )
