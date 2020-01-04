from unittest.mock import ANY, MagicMock, sentinel, patch

from pytest import fixture, mark, raises

from preacher.compilation.case import CaseCompiled, CaseCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request import RequestCompiler
from preacher.compilation.response import ResponseDescriptionCompiler

ctor_patch = patch(
    target='preacher.compilation.case.Case',
    return_value=sentinel.case,
)


@fixture
def compiler(req, res):
    return CaseCompiler(req, res)


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


def test_given_an_empty_object(compiler, req, res):
    compiled = compiler.compile({})
    assert compiled.label is None
    assert compiled.enabled is None
    assert compiled.request is None
    assert compiled.response is None

    req.compile.assert_not_called()
    res.compile.assert_not_called()


def test_creates_a_case(compiler, req, res):
    compiled = compiler.compile({
        'label': 'label',
        'enabled': False,
        'request': {'path': '/path'},
        'response': {'key': 'value'},
    })
    assert compiled.label == 'label'
    assert not compiled.enabled
    assert compiled.request is sentinel.request
    assert compiled.response is sentinel.response

    req.compile.assert_called_once_with({'path': '/path'})
    res.compile.assert_called_once_with({'key': 'value'})


@fixture
def initial_default():
    initial_default = MagicMock(CaseCompiled)
    initial_default.replace.return_value = sentinel.new_default
    return initial_default


@patch(
    target='preacher.compilation.case.CaseCompiler',
    return_value=sentinel.default_compiler,
)
def test_given_hollow_default(compiler_ctor, req, res, initial_default):
    compiler = CaseCompiler(req, res, initial_default)

    default = MagicMock(CaseCompiled, request=None, response=None)
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.default_compiler

    req.of_default.assert_not_called()
    res.of_default.assert_not_called()
    compiler_ctor.assert_called_once_with(
        request=req,
        response=res,
        default=ANY,
    )
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default


@patch(
    target='preacher.compilation.case.CaseCompiler',
    return_value=sentinel.default_compiler,
)
def test_given_filled_default(compiler_ctor, req, res, initial_default):
    compiler = CaseCompiler(req, res, initial_default)

    default = MagicMock(
        spec=CaseCompiled,
        request=sentinel.default_req,
        response=sentinel.default_res,
    )
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.default_compiler

    req.of_default.assert_called_once_with(sentinel.default_req)
    res.of_default.assert_called_once_with(sentinel.default_res)
    compiler_ctor.assert_called_once_with(
        request=sentinel.default_req_compiler,
        response=sentinel.default_res_compiler,
        default=ANY,
    )
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default


def test_compile_fixed(compiler):
    compiled = MagicMock(spec=CaseCompiled)
    compiled.fix.return_value = sentinel.fixed

    with patch.object(compiler, 'compile', return_value=compiled) as comp:
        fixed = compiler.compile_fixed(sentinel.obj)
    assert fixed is sentinel.fixed

    comp.assert_called_once_with(sentinel.obj)
    compiled.fix.assert_called_once_with()


def test_compile_default(compiler):
    with patch.object(
        target=compiler,
        attribute='compile',
        return_value=sentinel.compiled,
    ) as comp, patch.object(
        target=compiler,
        attribute='of_default',
        return_value=sentinel.compiler_of_default,
    ) as of_default:
        compiler_of_default = compiler.compile_default(sentinel.obj)
    assert compiler_of_default is sentinel.compiler_of_default

    comp.assert_called_once_with(sentinel.obj)
    of_default.assert_called_once_with(sentinel.compiled)
