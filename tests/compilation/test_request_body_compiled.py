from typing import Mapping
from unittest.mock import sentinel

from pytest import raises

from preacher.compilation.request_body import RequestBodyCompiled
from preacher.core.request import RequestBody


def test_interface():
    class _IncompleteRequestBodyCompiled(RequestBodyCompiled):
        def replace(self, other: RequestBodyCompiled) -> RequestBodyCompiled:
            return super().replace(other)

        def compile_and_replace(self, obj: Mapping) -> RequestBodyCompiled:
            return super().compile_and_replace(obj)

        def fix(self) -> RequestBody:
            return super().fix()

    compiled = _IncompleteRequestBodyCompiled()
    with raises(NotImplementedError):
        compiled.replace(sentinel.other)
    with raises(NotImplementedError):
        compiled.compile_and_replace({})
    with raises(NotImplementedError):
        compiled.fix()
