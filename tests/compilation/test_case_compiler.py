from unittest.mock import MagicMock, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.case import CaseCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request import RequestCompiler
from preacher.compilation.response import (
    ResponseDescriptionCompiler,
)


@fixture
def compiler(req, res):
    return CaseCompiler(req, res)


@fixture
def req():
    compiler = MagicMock(spec=RequestCompiler)
    compiler.compile.return_value = sentinel.request
    return compiler


@fixture
def res():
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
def test_given_invalid_values(value, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


def test_request_compilation_fails(compiler, req):
    req.compile.side_effect = CompilationError(
        message='message',
        path=[NamedNode('foo')],
    )
    with raises(CompilationError) as error_info:
        compiler.compile({})
    assert error_info.value.path == [NamedNode('request'), NamedNode('foo')]


def test_response_compilation_fails(compiler, res):
    res.compile.side_effect = CompilationError(
        message='message',
        path=[NamedNode('bar')],
    )
    with raises(CompilationError) as error_info:
        compiler.compile({'request': '/path'})
    assert error_info.value.path == [NamedNode('response'), NamedNode('bar')]


def test_given_an_empty_object(compiler, req, res):
    case = compiler.compile({})
    assert case.enabled
    assert case.request == sentinel.request
    assert case.response == sentinel.response

    req.compile.assert_called_once_with({})
    res.compile.assert_called_once_with({})


def test_creates_only_a_request(compiler, req):
    case = compiler.compile({'request': '/path'})
    assert case.label is None
    assert case.request == sentinel.request

    req.compile.assert_called_once_with('/path')


def test_creates_a_case(compiler, req, res):
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

    req.compile.assert_called_once_with({'path': '/path'})
    res.compile.assert_called_once_with({'key': 'value'})


def test_accepts_default_values(res):
    request_compiler = MagicMock(
        RequestCompiler,
        of_default=MagicMock(return_value=sentinel.foo),
    )
    compiler = CaseCompiler(request_compiler, res)
    default_compiler = compiler.of_default({})
    assert default_compiler.request_compiler == sentinel.foo
