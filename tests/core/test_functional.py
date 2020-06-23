from preacher.core.functional import identify


def test_identify():
    assert identify(None) is None
    assert identify(1) == 1
    assert identify('a') == 'a'
    assert identify([1, 2, 3]) == [1, 2, 3]
    assert identify(1, 2, key='value') == 1
