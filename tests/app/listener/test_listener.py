from unittest.mock import sentinel

from preacher.app.listener import Listener


def test_listener():
    listener = Listener()
    listener.on_end()
    listener.on_scenario(sentinel.scenario)
