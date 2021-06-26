from unittest.mock import sentinel

from preacher.core.scenario import Case

PKG = "preacher.core.scenario.case"


def test_default_construction(mocker):
    request_ctor = mocker.patch(f"{PKG}.Request")
    request_ctor.return_value = sentinel.request
    response_ctor = mocker.patch(f"{PKG}.ResponseDescription")
    response_ctor.return_value = sentinel.response

    case = Case()
    assert case.label is None
    assert case.enabled
    assert case.request is sentinel.request
    assert case.response is sentinel.response

    request_ctor.assert_called_once_with()
    response_ctor.assert_called_once_with()
