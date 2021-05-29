from preacher.core.value.impl.static import StaticValue


def test_static_value():
    value = StaticValue(1)
    assert issubclass(value.type, int)
    assert value.resolve() == 1
