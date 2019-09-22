from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.matcher import compile


def test_invalid_string():
    matcher = compile('_undefined')
    assert not matcher.matches(1)
    assert not matcher.matches('value')
    assert matcher.matches('_undefined')


@mark.parametrize('obj', (
    {},
    {'key1': 'value1', 'key2': 'value2'},
))
@mark.xfail(raises=CompilationError)
def test_invalid_mapping(obj):
    compile(obj)


def test_undefined_mapping():
    matcher = compile({'_undefined_key': 'value'})
    assert not matcher.matches(None)
    assert not matcher.matches(0)
    assert not matcher.matches('value')
    assert not matcher.matches({'key': 'value'})
    assert not matcher.matches({'_undefined_key': 'unmatch_value'})
    assert matcher.matches({'_undefined_key': 'value'})


def test_be_null():
    matcher = compile('be_null')
    assert matcher.matches(None)
    assert not matcher.matches(False)


def test_not_be_null():
    matcher = compile('not_be_null')
    assert not matcher.matches(None)
    assert matcher.matches('False')


def test_be_empty():
    matcher = compile('be_empty')
    assert not matcher.matches(None)
    assert not matcher.matches(0)
    assert matcher.matches('')
    assert not matcher.matches('A')
    assert matcher.matches([])
    assert not matcher.matches([1])


def test_have_length():
    matcher = compile({'have_length': 1})
    assert not matcher.matches(None)
    assert not matcher.matches(1)
    assert not matcher.matches('')
    assert not matcher.matches([])
    assert matcher.matches('A')
    assert matcher.matches([1])


def test_equal_to():
    matcher = compile({'equal': 1})
    assert not matcher.matches(0)
    assert not matcher.matches('1')
    assert matcher.matches(1)


def test_be_greater_than():
    matcher = compile({'be_greater_than': 0})
    assert not matcher.matches(-1)
    assert not matcher.matches(0)
    assert matcher.matches(1)


def test_be_greater_than_or_equal_to():
    matcher = compile({'be_greater_than_or_equal_to': 0})
    assert not matcher.matches(-1)
    assert matcher.matches(0)
    assert matcher.matches(1)


def test_be_less_than():
    matcher = compile({'be_less_than': 0})
    assert matcher.matches(-1)
    assert not matcher.matches(0)
    assert not matcher.matches(1)


def test_be_less_than_or_equal_to():
    matcher = compile({'be_less_than_or_equal_to': 0})
    assert matcher.matches(-1)
    assert matcher.matches(0)
    assert not matcher.matches(1)


def test_contain_string():
    matcher = compile({'contain_string': '0'})
    assert not matcher.matches(0)
    assert not matcher.matches('123')
    assert matcher.matches('21012')


def test_start_with():
    matcher = compile({'start_with': 'AB'})
    assert not matcher.matches(0)
    assert matcher.matches('ABC')
    assert not matcher.matches('ACB')


def test_end_with():
    matcher = compile({'end_with': 'BC'})
    assert not matcher.matches(0)
    assert matcher.matches('ABC')
    assert not matcher.matches('ACB')


def test_match_regexp():
    matcher = compile({'match_regexp': '^A*B$'})
    assert not matcher.matches('ACB')
    assert matcher.matches('B')
    with raises(TypeError):
        # TODO: Should return `False` when given not `str`.
        matcher.matches(0)


def test_be():
    matcher = compile({'be': 1})
    assert not matcher.matches(0)
    assert not matcher.matches('1')
    assert matcher.matches(1)


def test_not():
    matcher = compile({'not': 1})
    assert matcher.matches('A')
    assert matcher.matches(0)
    assert not matcher.matches(1)

    matcher = compile({'not': {'be_greater_than': 0}})
    assert matcher.matches(-1)
    assert matcher.matches(0)
    assert not matcher.matches(1)


def test_have_item():
    matcher = compile({'have_item': {'equal': 1}})
    assert not matcher.matches(None)
    assert not matcher.matches([])
    assert not matcher.matches([0, 'A'])
    assert matcher.matches([0, 1, 2])


def test_given_not_a_list_for_multiple_matchers():
    with raises(CompilationError) as error_info:
        compile({'contain': 1})
    assert str(error_info.value).endswith(': contain')


def test_contain():
    matcher = compile({
        'contain': [
            1,
            {'be_greater_than': 2},
            {'be_less_than': 3},
        ],
    })
    assert not matcher.matches([])
    assert not matcher.matches([1])
    assert not matcher.matches([1, 2, 4])
    assert matcher.matches([1, 4, 2])


def test_contain_in_any_order():
    matcher = compile({
        'contain_in_any_order': [
            1,
            {'be_greater_than': 2},
            {'be_less_than': 3},
        ],
    })
    assert not matcher.matches([])
    assert not matcher.matches([1])
    assert matcher.matches([1, 2, 4])
    assert matcher.matches([4, 1, 2])
    assert matcher.matches([1, 4, 2])
