"""Description compilation."""

from preacher.compilation.error import on_key
from preacher.compilation.type import compile_list, compile_mapping
from preacher.compilation.util import map_compile
from preacher.core.verification import Description
from .extraction import ExtractionCompiler
from .predicate import PredicateCompiler

_KEY_DESCRIBE = 'describe'
_KEY_SHOULD = 'should'


class DescriptionCompiler:

    def __init__(
        self,
        extraction: ExtractionCompiler,
        predicate: PredicateCompiler,
    ):
        self._extraction = extraction
        self._predicate = predicate

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
