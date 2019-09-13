from unittest.mock import MagicMock, sentinel

from pytest import raises

from preacher.compilation.extraction import compile
from preacher.compilation.error import CompilationError


def test_when_given_not_a_string():
    with raises(CompilationError) as error_info:
        compile({})
    assert str(error_info.value).endswith(' has 0')


def test_when_given_a_string():
    analyzer = MagicMock(jq=MagicMock(return_value=sentinel.value))
    value = compile('.foo').extract(analyzer)
    assert value == sentinel.value

    analyzer.jq.assert_called()


def test_when_given_a_jq():
    analyzer = MagicMock(jq=MagicMock(return_value=sentinel.value))
    value = compile({'jq': '.foo'}).extract(analyzer)
    assert value == sentinel.value

    analyzer.jq.assert_called()
