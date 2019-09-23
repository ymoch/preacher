from unittest.mock import MagicMock, call, patch

from pytest import mark, raises

from preacher.compilation.extraction import ExtractionCompiler
from preacher.compilation.error import CompilationError


MODULE = 'preacher.compilation.extraction'


@mark.parametrize('value, expected_suffix', (
    ({}, ' has 0'),
    ({'jq': '.xxx', 'multiple': 1}, ': multiple'),
    ({'jq': '.foo', 'cast_to': 1}, ' string: cast_to'),
    ({'jq': '.foo', 'cast_to': 'xxx'}, ': xxx: cast_to'),
))
def test_when_given_not_a_string(value, expected_suffix):
    with raises(CompilationError) as error_info:
        ExtractionCompiler().compile(value)
    assert str(error_info.value).endswith(expected_suffix)


@mark.parametrize('value, expected_call', (
    (
        '.foo',
        call('.foo', multiple=False, cast=None)
    ),
    (
        {'jq': '.foo'},
        call('.foo', multiple=False, cast=None),
    ),
    (
        {'jq': '.bar', 'multiple': False, 'cast_to': 'int'},
        call('.bar', multiple=False, cast=int),
    ),
    (
        {'jq': '.bar', 'multiple': True, 'cast_to': 'float'},
        call('.bar', multiple=True, cast=float),
    ),
))
def test_when_given_a_jq(value, expected_call):
    ctor = MagicMock()
    with patch.dict(f'{MODULE}._EXTRACTION_MAP', jq=ctor):
        ExtractionCompiler().compile(value)
    ctor.assert_has_calls([expected_call])


@mark.parametrize('value, expected_call', (
    (
        {'xpath': './foo'},
        call('./foo', multiple=False, cast=None),
    ),
    (
        {'xpath': './foo', 'multiple': False},
        call('./foo', multiple=False, cast=None),
    ),
    (
        {'xpath': './foo', 'multiple': True, 'cast_to': 'string'},
        call('./foo', multiple=True, cast=str),
    ),
))
def test_when_given_an_xpath(value, expected_call):
    ctor = MagicMock()
    with patch.dict(f'{MODULE}._EXTRACTION_MAP', xpath=ctor):
        ExtractionCompiler().compile(value)
    ctor.assert_has_calls([expected_call])
