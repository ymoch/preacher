from unittest.mock import MagicMock, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.case import CaseCompiler
from preacher.compilation.error import CompilationError
from preacher.compilation.request import RequestCompiler
from preacher.compilation.response_description import (
    ResponseDescriptionCompiler,
)


@fixture
def request_compiler() -> RequestCompiler:
    return MagicMock(
        spec=RequestCompiler,
        compile=MagicMock(return_value=sentinel.request),
    )


@fixture
def response_compiler() -> ResponseDescriptionCompiler:
    return MagicMock(
        spec=ResponseDescriptionCompiler,
        compile=MagicMock(return_value=sentinel.response_description),
    )


@mark.parametrize('value, expected_suffix', (
    ({'label': []}, ': label'),
    ({'request': []}, ': request'),
    ({'response': 'str'}, ': response'),
))
def test_given_invalid_values(
    value,
    expected_suffix,
    request_compiler,
    response_compiler,
):
    compiler = CaseCompiler(request_compiler, response_compiler)
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert str(error_info.value).endswith(expected_suffix)


@mark.parametrize('value, expected_suffix', (
    ({'request': []}, ': request'),
))
def test_given_invalid_default_values(
    value,
    expected_suffix,
    request_compiler,
    response_compiler,
):
    compiler = CaseCompiler(request_compiler, response_compiler)
    with raises(CompilationError) as error_info:
        compiler.of_default(value)
    assert str(error_info.value).endswith(expected_suffix)


def test_given_an_empty_object(request_compiler, response_compiler):
    compiler = CaseCompiler(request_compiler, response_compiler)
    case = compiler.compile({})
    assert case.request == sentinel.request
    assert case.response_description == sentinel.response_description

    request_compiler.compile.assert_called_once_with({})
    response_compiler.compile.assert_called_once_with({})
