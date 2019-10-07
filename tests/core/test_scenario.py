from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, sentinel

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

    case1.assert_called_once_with('base_url', retry=3, delay=2.0, timeout=5.0)
    case2.assert_called_once_with('base_url', retry=3, delay=2.0, timeout=5.0)


def test_given_subscenarios():
    condition1 = MagicMock(return_value=Verification.succeed())
    sentinel.result1.status = Status.SUCCESS
    case1 = MagicMock(return_value=sentinel.result1)
    sentinel.subresult1.status = Status.UNSTABLE
    subcase1 = MagicMock(return_value=sentinel.subresult1)
    sentinel.subresult2.status = Status.SUCCESS
    subcase2 = MagicMock(return_value=sentinel.subresult2)
    sentinel.subresult3.status = Status.FAILURE
    subcase3 = MagicMock(return_value=sentinel.subresult3)

    subscenario1 = Scenario(cases=[subcase1])
    subscenario2 = Scenario(cases=[subcase2, subcase3])
    scenario = Scenario(
        conditions=[condition1],
        cases=[case1],
        subscenarios=[subscenario1, subscenario2],
    )
    result = scenario.run(base_url='url', retry=5, delay=3.0, timeout=7.0)
    assert result.status == Status.FAILURE
    assert result.subscenarios[0].status == Status.UNSTABLE
    assert result.subscenarios[1].status == Status.FAILURE

    subcase1.assert_called_once_with('url', retry=5, delay=3.0, timeout=7.0)
    subcase2.assert_called_once_with('url', retry=5, delay=3.0, timeout=7.0)
    subcase3.assert_called_once_with('url', retry=5, delay=3.0, timeout=7.0)
