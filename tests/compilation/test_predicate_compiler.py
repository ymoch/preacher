from datetime import datetime, timezone
from unittest.mock import patch, sentinel

from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.predicate import PredicateCompiler
from preacher.core.status import Status


PACKAGE = 'preacher.compilation.predicate'
REQUEST_DATETIME = datetime(2019, 8, 28, tzinfo=timezone.utc)


@mark.parametrize('obj', (
    {},
    {'key1': 'value1', 'key2': 'value2'},
))
@mark.xfail(raises=CompilationError)
def test_invalid_mapping(obj):
    PredicateCompiler().compile(obj)


@mark.parametrize('obj, expected_path', (
    ({'before': 0}, ['before']),
    ({'after': 'invalid'}, ['after']),
))
def test_invalid_datetime_predicate(obj, expected_path):
    compiler = PredicateCompiler()
    with raises(CompilationError) as error_info:
        compiler.compile(obj)

    assert error_info.value.path == expected_path


@mark.parametrize('value, expected', (
    ('2019-08-27T00:00:00Z', Status.SUCCESS),
    ('2019-08-28T00:00:00Z', Status.SUCCESS),
    ('2019-08-29T00:00:00Z', Status.UNSTABLE),
))
def test_given_valid_before(value: str, expected: Status):
    compiler = PredicateCompiler()
    predicate = compiler.compile({'before': '1 day'})
    result = predicate(value, request_datetime=REQUEST_DATETIME)
    assert result.status == expected


@patch(f'{PACKAGE}.compile_matcher', return_value=sentinel.compile_matcher)
def test_given_matcher(matcher):
    compiler = PredicateCompiler()
    compiler.compile('matcher')
    matcher.assert_called_with('matcher')
