from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import List, Optional

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.functional import map_compile
from preacher.compilation.util.type import or_else
from preacher.core.verification import ResponseBodyDescription, Description
from .description import DescriptionCompiler

_KEY_DESCRIPTIONS = 'descriptions'


@dataclass(frozen=True)
class ResponseBodyDescriptionCompiled:
    descriptions: Optional[List[Description]] = None

    def replace(self, other: ResponseBodyDescriptionCompiled) -> ResponseBodyDescriptionCompiled:
        return ResponseBodyDescriptionCompiled(or_else(other.descriptions, self.descriptions))

    def fix(self) -> ResponseBodyDescription:
        return ResponseBodyDescription(self.descriptions)


class ResponseBodyDescriptionCompiler:

    def __init__(
        self,
        description: DescriptionCompiler,
        default: Optional[ResponseBodyDescriptionCompiled] = None,
    ):
        self._description = description
        self._default = default or ResponseBodyDescriptionCompiled()

    def compile(self, obj: object) -> ResponseBodyDescriptionCompiled:
        """
        `obj` should be a mapping or a list.
        An empty list results in an empty description.
        """

        if isinstance(obj, list):
            return self.compile({_KEY_DESCRIPTIONS: obj})
        if not isinstance(obj, Mapping):
            message = f'Must be a map or a list, given {type(obj)}'
            raise CompilationError(message)

        compiled = self._default

        descriptions_obj = obj.get(_KEY_DESCRIPTIONS)
        if descriptions_obj is not None:
            descriptions = self._compile_descriptions(descriptions_obj)
            compiled = replace(compiled, descriptions=descriptions)

        return compiled

    def of_default(
        self,
        default: ResponseBodyDescriptionCompiled
    ) -> ResponseBodyDescriptionCompiler:
        return ResponseBodyDescriptionCompiler(
            description=self._description,
            default=self._default.replace(default),
        )

    def _compile_descriptions(self, obj: object) -> List[Description]:
        if not isinstance(obj, list):
            obj = [obj]

        with on_key(_KEY_DESCRIPTIONS):
            return list(map_compile(self._description.compile, obj))
