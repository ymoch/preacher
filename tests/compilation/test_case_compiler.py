from unittest.mock import MagicMock, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.case import CaseCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request import RequestCompiler
from preacher.compilation.response_description import (
    ResponseDescriptionCompiler,
)


@fixture
def request_compiler():
    return MagicMock(
        spec=RequestCompiler,
        compile=MagicMock(return_value=sentinel.request),
    )


@fixture
def response_compiler():
    compiled = MagicMock()
    compiled.convert.return_value = sentinel.response

    compiler = MagicMock(spec=ResponseDescriptionCompiler)
    compiler.compile.return_value = compiled

    return compiler


@mark.parametrize('value, expected_path', (
    ('', []),
    ({'label': []}, [NamedNode('label')]),
    ({'enabled': []}, [NamedNode('enabled')]),
))
def test_given_invalid_values(
    value,
    expected_path,
    request_compiler,
    response_compiler,
):
    compiler = CaseCompiler(request_compiler, response_compiler)
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


def test_request_compilation_fails():
    request_compiler = MagicMock(
        spec=RequestCompiler,
        compile=MagicMock(
            side_effect=CompilationError(
                message='message',
                path=[NamedNode('foo')],
            )
        ),
    )
    compiler = CaseCompiler(request_compiler)
    with raises(CompilationError) as error_info:
        compiler.compile({})
    assert error_info.value.path == [NamedNode('request'), NamedNode('foo')]


def test_response_compilation_fails(request_compiler):
    response_compiler = MagicMock(
        spec=ResponseDescriptionCompiler,
        compile=MagicMock(
            side_effect=CompilationError(
                message='message',
                path=[NamedNode('bar')],
            ),
        ),
    )
    compiler = CaseCompiler(request_compiler, response_compiler)
    with raises(CompilationError) as error_info:
        compiler.compile({'request': '/path'})
    assert error_info.value.path == [NamedNode('response'), NamedNode('bar')]


def test_given_an_empty_object(request_compiler, response_compiler):
    compiler = CaseCompiler(request_compiler, response_compiler)
    case = compiler.compile({})
    assert case.enabled
    assert case.request == sentinel.request
    assert case.response == sentinel.response

    request_compiler.compile.assert_called_once_with({})
    response_compiler.compile.assert_called_once_with({})


def test_creates_only_a_request(request_compiler, response_compiler):
    compiler = CaseCompiler(request_compiler, response_compiler)
    case = compiler.compile({'request': '/path'})
    assert case.label is None
    assert case.request == sentinel.request

    request_compiler.compile.assert_called_once_with('/path')


def test_creates_a_case(request_compiler, response_compiler):
    compiler = CaseCompiler(request_compiler, response_compiler)
    case = compiler.compile({
        'label': 'label',
        'enabled': False,
        'request': {'path': '/path'},
        'response': {'key': 'value'},
    })
    assert case.label == 'label'
    assert not case.enabled
    assert case.request == sentinel.request
    assert case.response == sentinel.response

    request_compiler.compile.assert_called_once_with({'path': '/path'})
    response_compiler.compile.assert_called_once_with({'key': 'value'})


def test_accepts_default_values(response_compiler):
    request_compiler = MagicMock(
        RequestCompiler,
        of_default=MagicMock(return_value=sentinel.foo),
    )
    compiler = CaseCompiler(request_compiler, response_compiler)
    default_compiler = compiler.of_default({})
    assert default_compiler.request_compiler == sentinel.foo
