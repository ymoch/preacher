"""Context definitions."""

from contextlib import contextmanager
from typing import Iterator, MutableMapping

CONTEXT_KEY_STARTS = "starts"
CONTEXT_KEY_BASE_URL = "base_url"


class Context(MutableMapping[str, object]):
    def __init__(self, **kwargs):
        self._inner: MutableMapping[str, object] = dict(**kwargs)

    def __setitem__(self, key: str, value: object) -> None:
        self._inner[key] = value

    def __delitem__(self, key: str) -> None:
        del self._inner[key]

    def __getitem__(self, key: str) -> object:
        return self._inner[key]

    def __len__(self) -> int:
        return len(self._inner)

    def __iter__(self) -> Iterator[str]:
        return iter(self._inner)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Context):
            return False
        return self._inner == other._inner


@contextmanager
def closed_context(context: Context, **kwargs) -> Iterator[Context]:
    stored = {key: context[key] for key in kwargs if key in context}

    context.update(kwargs)
    yield context

    for key in kwargs:
        if key in stored:
            context[key] = stored[key]
        else:
            if key in context:
                del context[key]
