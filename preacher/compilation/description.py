"""Description compilation."""

from typing import Optional

from preacher.core.scenario import Description
from .error import on_key
from .extraction import ExtractionCompiler
from .predicate import PredicateCompiler
from .util import compile_list, compile_mapping, map_compile

_KEY_DESCRIBE = 'describe'
_KEY_SHOULD = 'should'


class DescriptionCompiler:

    def __init__(
        self,
        extraction: Optional[ExtractionCompiler] = None,
        predicate: Optional[PredicateCompiler] = None,
    ):
        self._extraction = extraction or ExtractionCompiler()
        self._predicate = predicate or PredicateCompiler()

    def compile(self, obj: object):
        """`obj` should be a mapping."""

        obj = compile_mapping(obj)

        extraction_obj = obj.get(_KEY_DESCRIBE)
        with on_key(_KEY_DESCRIBE):
            extractor = self._extraction.compile(extraction_obj)

        predicate_objs = compile_list(obj.get(_KEY_SHOULD, []))
        with on_key(_KEY_SHOULD):
            predicates = list(map_compile(
                self._predicate.compile,
                predicate_objs,
            ))

        return Description(extractor=extractor, predicates=predicates)
