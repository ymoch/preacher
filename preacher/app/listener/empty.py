from __future__ import annotations

from . import Listener


class EmptyListener(Listener):

    def __enter__(self) -> EmptyListener:
        return self

    def __exit__(self, ex_type, ex_value, trace) -> None:
        pass
