from unittest.mock import sentinel, ANY, call, NonCallableMock

from pytest import fixture

from preacher.core.scheduling import MergingListener
from preacher.core.status import Status
from preacher.presentation.listener import create_listener

PKG = "preacher.presentation.listener.factory"


@fixture
def merging_listener(mocker):
    merging = NonCallableMock(MergingListener)
    mocker.patch(f"{PKG}.MergingListener", return_value=merging)
    return merging


def test_create_listener_default(mocker, merging_listener):
    logging_factory = mocker.patch(f"{PKG}.create_logging_reporting_listener")
    logging_factory.return_value = sentinel.logging
    html_factory = mocker.patch(f"{PKG}.create_html_reporting_listener")

    create_listener()

    merging_listener.append.assert_called_once_with(sentinel.logging)
    logging_factory.assert_called_once_with(level=Status.SUCCESS, formatter=ANY)
    html_factory.assert_not_called()


def test_create_listener_with_all_parameters(mocker, merging_listener):
    logging_factory = mocker.patch(f"{PKG}.create_logging_reporting_listener")
    logging_factory.return_value = sentinel.logging
    html_factory = mocker.patch(f"{PKG}.create_html_reporting_listener")
    html_factory.return_value = sentinel.html

    create_listener(
        level=sentinel.level,
        formatter=sentinel.formatter,
        report_dir=sentinel.report_dir,
    )

    merging_listener.append.assert_has_calls((call(sentinel.logging), call(sentinel.html)))
    logging_factory.assert_called_once_with(level=sentinel.level, formatter=sentinel.formatter)
    html_factory.assert_called_once_with(sentinel.report_dir)
