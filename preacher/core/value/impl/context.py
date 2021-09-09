from typing import Optional, Type

from preacher.core.context import Context
from preacher.core.value import Value


class ContextualValue(Value[object]):
    def __init__(self, key: str):
        self._key = key

    @property
    def type(self) -> Type[object]:
        return object

    @property
    def key(self) -> str:
        return self._key

    def resolve(self, context: Optional[Context] = None) -> object:
        context = context or {}
        return context.get(self._key)
