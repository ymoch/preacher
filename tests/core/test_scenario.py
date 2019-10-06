from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, sentinel

from preacher.core.scenario import Scenario
from preacher.core.status import Status


def test_when_given_an_empty_scenario():
    scenario = Scenario(label=None, cases=[])
    with ThreadPoolExecutor(1) as executor:
        result = scenario.submit(executor, base_url='base_url').result()
    assert result.label is None
    assert result.status == Status.SKIPPED
    assert result.cases == []


def test_when_given_a_filled_scenario():
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
    assert result.cases == [sentinel.result1, sentinel.result2]

    case1.assert_called_once_with('base_url', retry=3, delay=2.0, timeout=5.0)
    case2.assert_called_once_with('base_url', retry=3, delay=2.0, timeout=5.0)
