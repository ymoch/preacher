from unittest.mock import NonCallableMock, sentinel

from pytest import raises

from preacher.compilation import CompilationError
from preacher.compilation.error import NamedNode
from preacher.compilation.request.request_body import (
    RequestBodyCompiled,
    UrlencodedRequestBodyCompiled,
)

PACKAGE = 'preacher.compilation.request.request_body'


def test_replace_given_another_type():
    original = UrlencodedRequestBodyCompiled()
    other = NonCallableMock(RequestBodyCompiled)
    replaced = original.replace(other)
    assert replaced is other


def test_replace_given_the_same_type():
    original = UrlencodedRequestBodyCompiled(data=sentinel.original_data)
    other = UrlencodedRequestBodyCompiled()
    replaced = original.replace(other)
    assert isinstance(replaced, UrlencodedRequestBodyCompiled)
    assert replaced.data is sentinel.original_data

    other = UrlencodedRequestBodyCompiled(data=sentinel.new_data)
    replaced = original.replace(other)
    assert isinstance(replaced, UrlencodedRequestBodyCompiled)
    assert replaced.data is sentinel.new_data


def test_compile_and_replace_empty():
    default = UrlencodedRequestBodyCompiled(data=sentinel.original_data)
    compiled = default.compile_and_replace({})
    assert isinstance(compiled, UrlencodedRequestBodyCompiled)
    assert compiled.data is sentinel.original_data


def test_compile_and_replace_given_invalid_data(mocker):
    compile_params = mocker.patch(f'{PACKAGE}.compile_url_params')
    compile_params.side_effect = CompilationError('m', node=NamedNode('x'))

    default = UrlencodedRequestBodyCompiled(data=sentinel.original_data)
    with raises(CompilationError) as error_info:
        default.compile_and_replace({'data': sentinel.data})
    assert error_info.value.path == [NamedNode('data'), NamedNode('x')]

    compile_params.assert_called_once_with(sentinel.data)


def test_compile_and_replace_given_valid_data(mocker):
    compile_params = mocker.patch(f'{PACKAGE}.compile_url_params')
    compile_params.return_value = sentinel.params

    default = UrlencodedRequestBodyCompiled(data=sentinel.original_data)
    compiled = default.compile_and_replace({'data': sentinel.data})
    assert isinstance(compiled, UrlencodedRequestBodyCompiled)
    assert compiled.data is sentinel.params

    compile_params.assert_called_once_with(sentinel.data)


def test_fix_empty(mocker):
    ctor = mocker.patch(f'{PACKAGE}.UrlencodedRequestBody')
    ctor.return_value = sentinel.fixed

    compiled = UrlencodedRequestBodyCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(params={})


def test_fix_filled(mocker):
    ctor = mocker.patch(f'{PACKAGE}.UrlencodedRequestBody')
    ctor.return_value = sentinel.fixed

    compiled = UrlencodedRequestBodyCompiled(data=sentinel.data)
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(params=sentinel.data)
