from preacher.core.util.functional import identity


def test_identify():
    assert identity(None) is None
    assert identity(1) == 1
    assert identity('a') == 'a'
    assert identity([1, 2, 3]) == [1, 2, 3]
    assert identity(1, 2, key='value') == 1
