from unittest.mock import sentinel

from pytest import mark, raises

from preacher.compilation.datetime import compile_datetime_format
from preacher.compilation.error import CompilationError
from preacher.core.datetime import ISO8601

PKG = "preacher.compilation.datetime"


@mark.parametrize("obj", (1, 1.2, complex(1, 2), [], {}))
def test_compile_datetime_format_given_invalid(obj):
    with raises(CompilationError):
        compile_datetime_format(obj)


@mark.parametrize("obj", (None, "iso8601", "ISO8601", "iSo8601"))
def test_compile_datetime_format_iso8601(obj):
    assert compile_datetime_format(obj) is ISO8601


@mark.parametrize("obj", ("", "%Y-%m-%s", "xxx"))
def test_compile_datetime_format_strftime(mocker, obj):
    ctor = mocker.patch(f"{PKG}.StrftimeFormat", return_value=sentinel.result)

    assert compile_datetime_format(obj) is sentinel.result
    ctor.assert_called_once_with(obj)
