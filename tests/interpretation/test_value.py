from pytest import raises

from preacher.interpretation.value import Value


def test_incomplete_value():
    class IncompleteValue(Value[object]):
        def apply_context(self, **kwargs) -> object:
            return super().apply_context(**kwargs)

    value = IncompleteValue()
    with raises(NotImplementedError):
        value.apply_context(key='value')
