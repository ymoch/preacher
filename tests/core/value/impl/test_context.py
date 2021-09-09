from preacher.core.value.impl.context import ContextualValue


def test_contextual_value():
    value = ContextualValue("foo")
    assert value.type is object
    assert value.resolve({}) is None
    assert value.resolve({"spam": "ham"}) is None
    assert value.resolve({"foo": "bar"}) == "bar"
