from unittest.mock import sentinel

from preacher.core.scheduling import create_scheduler

PKG = 'preacher.core.scheduling.factory'


def test_create_scheduler(mocker):
    requester_ctor = mocker.patch(f"{PKG}.Requester", return_value=sentinel.requester)
    unit_runner_ctor = mocker.patch(f"{PKG}.UnitRunner", return_value=sentinel.unit_runner)
    case_runner_ctor = mocker.patch(f"{PKG}.CaseRunner", return_value=sentinel.case_runner)
    runner_ctor = mocker.patch(f"{PKG}.ScenarioRunner", return_value=sentinel.runner)
    scheduler_ctor = mocker.patch(f"{PKG}.ScenarioScheduler", return_value=sentinel.scheduler)

    scheduler = create_scheduler(
        executor=sentinel.executor,
        listener=sentinel.listener,
        base_url=sentinel.base_url,
        timeout=sentinel.timeout,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    assert scheduler is sentinel.scheduler

    requester_ctor.assert_called_once_with(base_url=sentinel.base_url, timeout=sentinel.timeout)
    unit_runner_ctor.assert_called_once_with(
        requester=sentinel.requester,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    case_runner_ctor.assert_called_once_with(
        unit_runner=sentinel.unit_runner,
        listener=sentinel.listener,
    )
    runner_ctor.assert_called_once_with(
        executor=sentinel.executor,
        case_runner=sentinel.case_runner,
    )
    scheduler_ctor.assert_called_once_with(runner=sentinel.runner, listener=sentinel.listener)
