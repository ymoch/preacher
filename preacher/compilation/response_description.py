"""Response description compilations."""

from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.description import Description
from preacher.core.response_description import ResponseDescription
from .error import CompilationError
from .description import DescriptionCompiler
from .predicate import PredicateCompiler
from .util import map_on_key


_KEY_STATUS_CODE = 'status_code'
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

    def compile(self, obj: Mapping) -> ResponseDescription:
        status_code_predicate_objs = obj.get(_KEY_STATUS_CODE, [])
        if not isinstance(status_code_predicate_objs, list):
            status_code_predicate_objs = [status_code_predicate_objs]
        status_code_predicates = list(map_on_key(
            key=_KEY_STATUS_CODE,
            func=self._predicate_compiler.compile,
            items=status_code_predicate_objs,
        ))

        body_description_objs = obj.get(_KEY_BODY, [])
        if isinstance(body_description_objs, Mapping):
            body_description_objs = [body_description_objs]
        if not isinstance(body_description_objs, list):
            raise CompilationError(
                message='ResponseDescription.body must be a list or a mapping',
                path=[_KEY_BODY],
            )
        body_descriptions = list(map_on_key(
            key=_KEY_BODY,
            func=self._compile_description,
            items=body_description_objs,
        ))

        return ResponseDescription(
            status_code_predicates=status_code_predicates,
            body_descriptions=body_descriptions,
        )

    def _compile_description(self, obj: Any) -> Description:
        if not isinstance(obj, Mapping):
            raise CompilationError('Description must be a mapping')
        return self._description_compiler.compile(obj)
