from preacher.compilation.matcher import compile

from pytest import raises


def test_invalid_string():
    matcher = compile('_undefined')
    assert not matcher.matches(1)
    assert not matcher.matches('value')
    assert matcher.matches('_undefined')


def test_invalid_mapping():
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
