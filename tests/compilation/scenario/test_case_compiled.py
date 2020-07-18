from unittest.mock import NonCallableMock, sentinel

from preacher.compilation.request import RequestCompiled
from preacher.compilation.scenario.case import CaseCompiled
from preacher.compilation.verification.response import (
    ResponseDescriptionCompiled,
)

PKG = 'preacher.compilation.scenario.case'


def test_replace():
    initial = CaseCompiled(
        label=sentinel.initial_label,
        enabled=sentinel.initial_enabled,
        request=sentinel.initial_request,
        response=sentinel.initial_response,
    )

    other = CaseCompiled()
    replaced = initial.replace(other)
    assert replaced.label is sentinel.initial_label
    assert replaced.enabled is sentinel.initial_enabled
    assert replaced.request is sentinel.initial_request
    assert replaced.response is sentinel.initial_response

    other = CaseCompiled(
        label=sentinel.label,
        enabled=sentinel.enabled,
        request=sentinel.request,
        response=sentinel.response,
    )
    replaced = initial.replace(other)
    assert replaced.label is sentinel.label
    assert replaced.enabled is sentinel.enabled
    assert replaced.request is sentinel.request
    assert replaced.response is sentinel.response


def test_fix_hollow(mocker):
    ctor = mocker.patch(f'{PKG}.Case', return_value=sentinel.fixed)

    compiled = CaseCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        label=None,
        enabled=True,
        conditions=[],
        request=None,
        response=None,
    )


def test_fix_filled(mocker):
    ctor = mocker.patch(f'{PKG}.Case', return_value=sentinel.fixed)

    request = NonCallableMock(RequestCompiled)
    request.fix.return_value = sentinel.request

    response = NonCallableMock(ResponseDescriptionCompiled)
    response.fix.return_value = sentinel.response

    compiled = CaseCompiled(
        label=sentinel.label,
        enabled=sentinel.enabled,
        conditions=sentinel.conditions,
        request=request,
        response=response,
    )
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        label=sentinel.label,
        enabled=sentinel.enabled,
        conditions=sentinel.conditions,
        request=sentinel.request,
        response=sentinel.response,
    )
    request.fix.assert_called_once_with()
    response.fix.assert_called_once_with()
