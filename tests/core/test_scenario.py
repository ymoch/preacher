from concurrent.futures import ThreadPoolExecutor
from unittest.mock import ANY, MagicMock, patch, sentinel

from preacher.core.context import Context
from preacher.core.description import Description
from preacher.core.scenario import Scenario
from preacher.core.status import Status
from preacher.core.verification import Verification


def test_given_an_empty_scenario():
    scenario = Scenario(label=None, cases=[])
    with ThreadPoolExecutor(1) as executor:
        result = scenario.submit(executor, base_url='base_url').result()
    assert result.label is None
    assert result.status == Status.SKIPPED
    assert list(result.cases) == []


def test_given_a_filled_scenario():
    sentinel.result1.status = Status.UNSTABLE
    case1 = MagicMock(return_value=sentinel.result1)
    sentinel.result2.status = Status.SUCCESS
    case2 = MagicMock(return_value=sentinel.result2)

    scenario = Scenario(label='label', cases=[case1, case2])
    result = scenario.run(
        base_url='base_url',
        retry=3,
        delay=2.0,
        timeout=5.0,
    )
    assert result.label == 'label'
    assert result.status == Status.UNSTABLE
    assert list(result.cases) == [sentinel.result1, sentinel.result2]

    case1.assert_called_once_with(
        'base_url', retry=3, delay=2.0, timeout=5.0, listener=ANY,
    )
    case2.assert_called_once_with(
        'base_url', retry=3, delay=2.0, timeout=5.0, listener=ANY,
    )


@patch('preacher.core.scenario.Context')
def test_given_subscenarios(context_ctor):
    context = MagicMock(spec=Context)
    context.analyze.return_value = sentinel.context_analyzer
    context_ctor.return_value = context

    condition1 = MagicMock(Description, verify=MagicMock(
        return_value=Verification.succeed()
    ))
    condition2 = MagicMock(Description, verify=MagicMock(
        return_value=Verification(status=Status.UNSTABLE)
    ))
    condition3 = MagicMock(Description, verify=MagicMock(
        return_value=Verification.succeed()
    ))
    condition4 = MagicMock(Description, verify=MagicMock(
        return_value=Verification(status=Status.FAILURE)
    ))
    condition5 = MagicMock(Description, verify=MagicMock(
        return_value=Verification(status=Status.UNSTABLE)
    ))

    sentinel.result1.status = Status.SUCCESS
    case1 = MagicMock(return_value=sentinel.result1)
    sentinel.subresult1.status = Status.UNSTABLE
    subcase1 = MagicMock(return_value=sentinel.subresult1)
    sentinel.subresult2.status = Status.SUCCESS
    subcase2 = MagicMock(return_value=sentinel.subresult2)
    sentinel.subresult3.status = Status.FAILURE
    subcase3 = MagicMock(return_value=sentinel.subresult3)
    sentinel.subresult4.status = Status.SUCCESS
    subcase4 = MagicMock(return_value=sentinel.subresult4)
    sentinel.subresult5.status = Status.SUCCESS
    subcase5 = MagicMock(return_value=sentinel.subresult5)

    subscenario1 = Scenario(cases=[subcase1])
    subscenario2 = Scenario(cases=[subcase2, subcase3])
    subscenario3 = Scenario(
        conditions=[condition2, condition3],
        cases=[subcase4],
    )
    subscenario4 = Scenario(
        conditions=[condition4, condition5],
        cases=[subcase5],
    )
    scenario = Scenario(
        conditions=[condition1],
        cases=[case1],
        subscenarios=[subscenario1, subscenario2, subscenario3, subscenario4],
    )

    result = scenario.run(
        base_url='url',
        retry=5,
        delay=3.0,
        timeout=7.0,
        listener=sentinel.listener,
    )
    assert result.status == Status.FAILURE
    assert result.subscenarios[0].status == Status.UNSTABLE
    assert result.subscenarios[1].status == Status.FAILURE
    assert result.subscenarios[2].status == Status.SKIPPED
    assert (
        result.subscenarios[2].conditions.children[0].status == Status.UNSTABLE
    )
    assert (
        result.subscenarios[2].conditions.children[1].status == Status.SUCCESS
    )
    assert result.subscenarios[3].status == Status.FAILURE
    assert (
        result.subscenarios[3].conditions.children[0].status == Status.FAILURE
    )
    assert (
        result.subscenarios[3].conditions.children[1].status == Status.UNSTABLE
    )

    context_ctor.assert_called_with(base_url='url')
    condition1.verify.assert_called_with(sentinel.context_analyzer)
    subcase1.assert_called_once_with(
        'url', retry=5, delay=3.0, timeout=7.0, listener=sentinel.listener,
    )
    subcase2.assert_called_once_with(
        'url', retry=5, delay=3.0, timeout=7.0, listener=sentinel.listener,
    )
    subcase3.assert_called_once_with(
        'url', retry=5, delay=3.0, timeout=7.0, listener=sentinel.listener,
    )
    subcase4.assert_not_called()
    subcase5.assert_not_called()
