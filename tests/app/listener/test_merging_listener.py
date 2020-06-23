from unittest.mock import MagicMock, sentinel

from pytest import fixture

from preacher.app.listener.merging import MergingListener
from preacher.core.runner import Listener


@fixture
def listeners():
    return [MagicMock(Listener), MagicMock(Listener)]


@fixture
def merging_listener(listeners) -> MergingListener:
    merging_listener = MergingListener()
    for listener in listeners:
        merging_listener.append(listener)
    return merging_listener


def test_on_response(merging_listener, listeners):
    merging_listener.on_response(sentinel.response)
    for listener in listeners:
        listener.on_response.assert_called_once_with(sentinel.response)


def test_on_scenario(merging_listener, listeners):
    merging_listener.on_scenario(sentinel.scenario)
    for listener in listeners:
        listener.on_scenario.assert_called_once_with(sentinel.scenario)


def test_on_end(merging_listener, listeners):
    merging_listener.on_end()
    for listener in listeners:
        listener.on_end.assert_called_once_with()
