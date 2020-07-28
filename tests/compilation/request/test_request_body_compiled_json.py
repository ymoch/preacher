from unittest.mock import NonCallableMock, sentinel

from preacher.compilation.request.request_body import JsonRequestBodyCompiled
from preacher.compilation.request.request_body import RequestBodyCompiled

PACKAGE = 'preacher.compilation.request.request_body'


def test_replace():
    original = JsonRequestBodyCompiled(data=sentinel.original_data)
    replacer = JsonRequestBodyCompiled()
    replaced = original.replace(replacer)
    assert isinstance(replaced, JsonRequestBodyCompiled)
    assert replaced.data is sentinel.original_data

    replacer = JsonRequestBodyCompiled(data=sentinel.new_data)
    replaced = original.replace(replacer)
    assert isinstance(replaced, JsonRequestBodyCompiled)
    assert replaced.data is sentinel.new_data

    replacer = JsonRequestBodyCompiled(data=None)
    replaced = original.replace(replacer)
    assert isinstance(replaced, JsonRequestBodyCompiled)
    assert replaced.data is None

    replacer = NonCallableMock(RequestBodyCompiled)
    replaced = original.replace(replacer)
    assert replaced is replacer


def test_compile_and_replace():
    compiled = JsonRequestBodyCompiled(data=sentinel.original_data)

    replaced = compiled.compile_and_replace({})
    assert replaced is compiled

    replaced = compiled.compile_and_replace({'data': sentinel.new_data})
    assert isinstance(replaced, JsonRequestBodyCompiled)
    assert replaced.data is sentinel.new_data


def test_fix_hollowed(mocker):
    ctor = mocker.patch(f'{PACKAGE}.JsonRequestBody')
    ctor.return_value = sentinel.result

    compiled = JsonRequestBodyCompiled()
    result = compiled.fix()
    assert result is sentinel.result

    ctor.assert_called_once_with(data=None)


def test_fix_filled(mocker):
    ctor = mocker.patch(f'{PACKAGE}.JsonRequestBody')
    ctor.return_value = sentinel.result

    compiled = JsonRequestBodyCompiled(data=sentinel.data)
    result = compiled.fix()
    assert result is sentinel.result

    ctor.assert_called_once_with(data=sentinel.data)
