"""Response description compilations."""

from collections.abc import Mapping
from typing import Any, Optional, Iterator

from preacher.core.description import Description
from preacher.core.response_description import ResponseDescription
from .body_description import BodyDescriptionCompiler
from .error import CompilationError
from .description import DescriptionCompiler
from .predicate import PredicateCompiler
from .util import map_on_key, run_on_key


_KEY_STATUS_CODE = 'status_code'
_KEY_HEADERS = 'headers'
_KEY_BODY = 'body'


class ResponseDescriptionCompiler:

    def __init__(
        self,
        predicate_compiler: Optional[PredicateCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
    ):
        self._predicate_compiler = predicate_compiler or PredicateCompiler()
        self._description_compiler = (
            description_compiler
            or DescriptionCompiler(
                predicate_compiler=self._predicate_compiler
            )
        )

    def compile(self, obj: Any) -> ResponseDescription:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        status_code_predicate_objs = obj.get(_KEY_STATUS_CODE, [])
        if not isinstance(status_code_predicate_objs, list):
            status_code_predicate_objs = [status_code_predicate_objs]
        status_code_predicates = list(map_on_key(
            key=_KEY_STATUS_CODE,
            func=self._predicate_compiler.compile,
            items=status_code_predicate_objs,
        ))

        headers_descriptions = list(self._compile_descs(_KEY_HEADERS, obj))

        body_description = run_on_key(
            _KEY_BODY,
            BodyDescriptionCompiler(
                description_compiler=self._description_compiler,
            ).compile,
            obj.get(_KEY_BODY, {}),
        )

        return ResponseDescription(
            status_code_predicates=status_code_predicates,
            headers_descriptions=headers_descriptions,
            body_description=body_description,
        )

    def _compile_descs(self, key: str, obj: Any) -> Iterator[Description]:
        desc_objs = obj.get(key, [])
        if isinstance(desc_objs, Mapping):
            desc_objs = [desc_objs]
        if not isinstance(desc_objs, list):
            message = f'ResponseDescription.{key} must be a list or a mapping'
            raise CompilationError(message=message, path=[key])

        return map_on_key(key, self._description_compiler.compile, desc_objs)
