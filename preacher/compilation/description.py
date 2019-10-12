"""Description compilation."""

from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.description import Description
from .error import CompilationError
from .predicate import PredicateCompiler
from .extraction import ExtractionCompiler
from .util import run_on_key, map_on_key


_KEY_DESCRIBE = 'describe'
_KEY_SHOULD = 'should'


class DescriptionCompiler:

    def __init__(
        self,
        extraction_compiler: Optional[ExtractionCompiler] = None,
        predicate_compiler: Optional[PredicateCompiler] = None,
    ):
        self._extraction_compiler = extraction_compiler or ExtractionCompiler()
        self._predicate_compiler = predicate_compiler or PredicateCompiler()

    def compile(self, obj: Any):
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        extraction_obj = obj.get(_KEY_DESCRIBE)
        extractor = run_on_key(
            _KEY_DESCRIBE,
            self._extraction_compiler.compile,
            extraction_obj
        )

        predicate_objs = obj.get(_KEY_SHOULD, [])
        if not isinstance(predicate_objs, list):
            predicate_objs = [predicate_objs]
        predicates = list(map_on_key(
            _KEY_SHOULD,
            self._predicate_compiler.compile,
            predicate_objs,
        ))

        return Description(extractor=extractor, predicates=predicates)
