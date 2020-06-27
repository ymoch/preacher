from unittest.mock import MagicMock, sentinel

from preacher.core.scenario.description import Description
from preacher.core.scenario.response_body import ResponseBodyDescription
from preacher.core.scenario.status import Status
from preacher.core.scenario.verification import Verification


def test_given_invalid_body():
    descriptions = [
        MagicMock(Description, verify=MagicMock(
            return_value=Verification.succeed()
        )),
    ]
    analyze = MagicMock(side_effect=RuntimeError('parse error'))

    description = ResponseBodyDescription(
        descriptions=descriptions,
        analyze=analyze,
    )
    verification = description.verify(sentinel.response_body)
    assert verification.status == Status.FAILURE
    assert verification.message.endswith('parse error')

    analyze.assert_called_once_with(sentinel.response_body)
    descriptions[0].verify.assert_not_called()


def test_given_descriptions():
    descriptions = [
        MagicMock(Description, verify=MagicMock(
            return_value=Verification(status=Status.UNSTABLE)
        )),
        MagicMock(Description, verify=MagicMock(
            return_value=Verification.succeed()
        )),
    ]
    analyze = MagicMock(return_value=sentinel.body)
    description = ResponseBodyDescription(
        descriptions=descriptions,
        analyze=analyze,
    )
    verification = description.verify(sentinel.response_body, k='v')
    assert verification.status == Status.UNSTABLE
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.SUCCESS

    analyze.assert_called_once_with(sentinel.response_body)
    for description in descriptions:
        description.verify.assert_called_once_with(sentinel.body, k='v')