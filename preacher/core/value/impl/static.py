from typing import Type, Optional

from preacher.core.value import Value, T, ValueContext


class StaticValue(Value[T]):

    def __init__(self, value: T):
        self._value = value

    @property
    def type(self) -> Type[T]:
        return type(self._value)

    def resolve(self, context: Optional[ValueContext] = None) -> T:
        return self._value
