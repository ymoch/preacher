from unittest.mock import MagicMock, sentinel, patch

from pytest import fixture, mark, raises

from preacher.compilation.case import CaseCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request import RequestCompiler
from preacher.compilation.response import ResponseDescriptionCompiler
from preacher.core.case import Case


ctor_patch = patch(
    target='preacher.compilation.case.Case',
    return_value=sentinel.case,
)


@fixture
def compiler(req, res):
    default = MagicMock(Case)
    default.label = sentinel.default_label
    default.enabled = sentinel.default_enabled
    default.request = sentinel.default_request
    default.response = sentinel.default_response

    return CaseCompiler(req, res, default)


@fixture
def req():
    compiler = MagicMock(spec=RequestCompiler)
    compiler.compile.return_value = sentinel.request
    compiler.of_default.return_value = sentinel.default_req_compiler
    return compiler


@fixture
def res():
    compiler = MagicMock(spec=ResponseDescriptionCompiler)
    compiler.compile.return_value = sentinel.response
    compiler.of_default.return_value = sentinel.default_res_compiler
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
        compiler.compile({'request': '/path'})
    assert error_info.value.path == [NamedNode('request'), NamedNode('foo')]

    req.compile.assert_called_once_with('/path')


def test_response_compilation_fails(compiler, res):
    res.compile.side_effect = CompilationError(
        message='message',
        path=[NamedNode('bar')],
    )
    with raises(CompilationError) as error_info:
        compiler.compile({'response': 'res'})
    assert error_info.value.path == [NamedNode('response'), NamedNode('bar')]

    res.compile.assert_called_once_with('res')


@ctor_patch
def test_given_an_empty_object(ctor, compiler, req, res):
    case = compiler.compile({})
    assert case is sentinel.case

    ctor.assert_called_once_with(
        label=sentinel.default_label,
        enabled=sentinel.default_enabled,
        request=sentinel.default_request,
        response=sentinel.default_response,
    )
    req.compile.assert_not_called()
    res.compile.assert_not_called()


@ctor_patch
def test_creates_a_case(ctor, compiler, req, res):
    case = compiler.compile({
        'label': 'label',
        'enabled': False,
        'request': {'path': '/path'},
        'response': {'key': 'value'},
    })
    assert case is sentinel.case

    ctor.assert_called_once_with(
        label='label',
        enabled=False,
        request=sentinel.request,
        response=sentinel.response
    )
    req.compile.assert_called_once_with({'path': '/path'})
    res.compile.assert_called_once_with({'key': 'value'})


@patch(
    target='preacher.compilation.case.CaseCompiler',
    return_value=sentinel.default_compiler,
)
def test_accepts_default_values(compiler_ctor, compiler, req, res):
    default = MagicMock(spec=Case)
    default.request = sentinel.request
    default.response = sentinel.response

    default_compiler = compiler.of_default(default)
    assert default_compiler is sentinel.default_compiler

    compiler_ctor.assert_called_once_with(
        request=sentinel.default_req_compiler,
        response=sentinel.default_res_compiler,
        default=default,
    )
    req.of_default.assert_called_once_with(sentinel.request)
    res.of_default.assert_called_once_with(sentinel.response)
