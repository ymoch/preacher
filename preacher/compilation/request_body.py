from __future__ import annotations

from preacher.core.scenario import RequestBody


class RequestBodyCompiled:

    def fix(self) -> RequestBody:
        raise NotImplementedError()


class RequestBodyCompiler:

    def compile(self, obj: object) -> RequestBody:
        raise NotImplementedError()

    def of_default(self, default: RequestBodyCompiled) -> RequestBodyCompiler:
        return self
