from unittest.mock import patch, sentinel

from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.matcher import compile
from preacher.core.interpretation.datetime import interpret_datetime
from preacher.core.scenario.hamcrest import after, before
from preacher.core.scenario.matcher import match
from preacher.core.scenario.status import Status

PACKAGE = 'preacher.compilation.matcher'

SUCCESS = Status.SUCCESS
UNSTABLE = Status.UNSTABLE
FAILURE = Status.FAILURE


@mark.parametrize('obj', [
    {},
    {'key1': 'value1', 'key2': 'value2'},
])
def test_invalid_mapping(obj):
    with raises(CompilationError):
        compile(obj)


@mark.parametrize('compiled, verified, expected_status', [
    ('_undefined_string', 1, UNSTABLE),
    ('_undefined_string', 'value', UNSTABLE),
    ('_undefined_string', '_undefined_string', SUCCESS),
    ({'_undefined_key': 'value'}, None, UNSTABLE),
    ({'_undefined_key': 'value'}, 0, UNSTABLE),
    ({'_undefined_key': 'value'}, 'value', UNSTABLE),
    ({'_undefined_key': 'value'}, {'key': 'value'}, UNSTABLE),
    ({'_undefined_key': 'value'}, {'_undefined_key': '_'}, UNSTABLE),
    ({'_undefined_key': 'value'}, {'_undefined_key': 'value'}, SUCCESS),
    ('be_null', None, SUCCESS),
    ('be_null', False, UNSTABLE),
    ('not_be_null', None, UNSTABLE),
    ('not_be_null', False, SUCCESS),
    ('be_empty', None, UNSTABLE),
    ('be_empty', 0, UNSTABLE),
    ('be_empty', '', SUCCESS),
    ('be_empty', 'A', UNSTABLE),
    ('be_empty', [], SUCCESS),
    ('be_empty', [0], UNSTABLE),
    ({'have_length': 1}, None, UNSTABLE),
    ({'have_length': 1}, 1, UNSTABLE),
    ({'have_length': 1}, '', UNSTABLE),
    ({'have_length': 1}, [], UNSTABLE),
    ({'have_length': 1}, 'A', SUCCESS),
    ({'have_length': 1}, [0], SUCCESS),
    ({'equal': 1}, 0, UNSTABLE),
    ({'equal': 1}, 1, SUCCESS),
    ({'equal': 1}, '1', UNSTABLE),
    ({'be_greater_than': 0}, -1, UNSTABLE),
    ({'be_greater_than': 0}, 0, UNSTABLE),
    ({'be_greater_than': 0}, 1, SUCCESS),
    ({'be_greater_than_or_equal_to': 0}, -1, UNSTABLE),
    ({'be_greater_than_or_equal_to': 0}, 0, SUCCESS),
    ({'be_greater_than_or_equal_to': 0}, 1, SUCCESS),
    ({'be_less_than': 0}, -1, SUCCESS),
    ({'be_less_than': 0}, 0, UNSTABLE),
    ({'be_less_than': 0}, 1, UNSTABLE),
    ({'be_less_than_or_equal_to': 0}, -1, SUCCESS),
    ({'be_less_than_or_equal_to': 0}, 0, SUCCESS),
    ({'be_less_than_or_equal_to': 0}, 1, UNSTABLE),
    ({'contain_string': '0'}, 0, UNSTABLE),
    ({'contain_string': '0'}, '123', UNSTABLE),
    ({'contain_string': '0'}, '21012', SUCCESS),
    ({'start_with': 'AB'}, 0, UNSTABLE),
    ({'start_with': 'AB'}, 'ABC', SUCCESS),
    ({'start_with': 'AB'}, 'CAB', UNSTABLE),
    ({'end_with': 'BC'}, 0, UNSTABLE),
    ({'end_with': 'BC'}, 'ABC', SUCCESS),
    ({'end_with': 'BC'}, 'BCA', UNSTABLE),
    ({'match_regexp': '^A*B$'}, 'ACB', UNSTABLE),
    ({'match_regexp': '^A*B$'}, 'B', SUCCESS),
    ({'match_regexp': '^A*B$'}, 0, FAILURE),  # TODO: Should be UNSTABLE.
    ({'be': 1}, 0, UNSTABLE),
    ({'be': 1}, '1', UNSTABLE),
    ({'be': 1}, 1, SUCCESS),
    ({'not': 1}, 'A', SUCCESS),
    ({'not': 1}, 0, SUCCESS),
    ({'not': 1}, 1, UNSTABLE),
    ({'not': {'be_greater_than': 0}}, -1, SUCCESS),
    ({'not': {'be_greater_than': 0}}, 0, SUCCESS),
    ({'not': {'be_greater_than': 0}}, 1, UNSTABLE),
    ({'have_item': {'equal': 1}}, None, UNSTABLE),
    ({'have_item': {'equal': 1}}, [], UNSTABLE),
    ({'have_item': {'equal': 1}}, [0, 'A'], UNSTABLE),
    ({'have_item': {'equal': 1}}, [0, 1, 2], SUCCESS),
    ({'contain': 1}, [], UNSTABLE),
    ({'contain': 1}, [1], SUCCESS),
    ({'contain': 1}, [1, 2], UNSTABLE),
    ({'contain': 1}, [2, 3], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 2, 4], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2], SUCCESS),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2, 3], UNSTABLE),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [], UNSTABLE),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1], UNSTABLE),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 2, 4], SUCCESS),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [4, 1, 2], SUCCESS),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2], SUCCESS),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2, 3], UNSTABLE),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [], UNSTABLE),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1], UNSTABLE),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 2, 4], SUCCESS),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [4, 1, 2], SUCCESS),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2], SUCCESS),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2, 3], SUCCESS),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 1, UNSTABLE),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 2, SUCCESS),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 3, UNSTABLE),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 1, SUCCESS),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 2, UNSTABLE),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 3, UNSTABLE),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 4, SUCCESS),
    ('anything', None, SUCCESS),
    ('anything', 1, SUCCESS),
    ('anything', [1], SUCCESS),
    ('anything', {'key': 'value'}, SUCCESS),
])
def test_verification(compiled, verified, expected_status):
    assert match(compile(compiled), verified).status == expected_status


@patch(f'{PACKAGE}.ValueMatcher', return_value=sentinel.matcher)
@patch(f'{PACKAGE}.value_of', return_value=sentinel.value)
@mark.parametrize('compiled, expected_value, expected_hamcrest_factory', [
    ({'be_before': 'now'}, 'now', before),
    ({'be_after': '1 second'}, '1 second', after),
])
def test_verification_with_datetime(
    value_of,
    matcher_ctor,
    compiled,
    expected_value,
    expected_hamcrest_factory,
):
    actual = compile(compiled)
    assert actual == sentinel.matcher

    value_of.assert_called_once_with(expected_value)
    matcher_ctor.assert_called_once_with(
        expected_hamcrest_factory,
        sentinel.value,
        interpret=interpret_datetime,
    )
