from typing import Optional, Type

from pytest import raises

from preacher.core.value import Value, ValueContext


def test_incomplete_value():
    class IncompleteValue(Value[object]):
        @property
        def type(self) -> Type[object]:
            return super().type

        def resolve(self, context: Optional[ValueContext] = None) -> object:
            return super().resolve(context)

    value = IncompleteValue()
    with raises(NotImplementedError):
        assert value.type == object
    with raises(NotImplementedError):
        value.resolve(ValueContext())
