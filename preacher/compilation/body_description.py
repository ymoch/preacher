from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.body_description import BodyDescription
from .description import DescriptionCompiler
from .error import CompilationError
from .util import map_on_key


_KEY_DESCRIPTIONS = 'descriptions'


class BodyDescriptionCompiler:

    def __init__(
        self,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._description_compiler = (
            description_compiler or DescriptionCompiler()
        )

    def compile(self, obj: Any) -> BodyDescription:
        """
        `obj` should be a mapping or a list.
        An empty list results in an empty description.
        """

        if isinstance(obj, list):
            return self.compile({_KEY_DESCRIPTIONS: obj})

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping or a list')

        desc_objs = obj.get(_KEY_DESCRIPTIONS)
        if desc_objs is None:
            # Compile as a description to be compatible.
            description = self._description_compiler.compile(obj)
            return BodyDescription(descriptions=[description])

        if not isinstance(desc_objs, list):
            desc_objs = [desc_objs]

        descriptions = list(map_on_key(
            _KEY_DESCRIPTIONS,
            self._description_compiler.compile,
            desc_objs,
        ))
        return BodyDescription(descriptions=descriptions)
