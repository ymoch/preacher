"""Description compilation."""

from typing import Optional

from preacher.core.scenario import AnalysisDescription
from .error import on_key
from .extraction import ExtractionCompiler
from .predicate import PredicateCompiler
from .util import compile_mapping, map_compile

_KEY_DESCRIBE = 'describe'
_KEY_SHOULD = 'should'


class AnalysisDescriptionCompiler:

    def __init__(
        self,
        extraction_compiler: Optional[ExtractionCompiler] = None,
        predicate_compiler: Optional[PredicateCompiler] = None,
    ):
        self._extraction_compiler = extraction_compiler or ExtractionCompiler()
        self._predicate_compiler = predicate_compiler or PredicateCompiler()

    def compile(self, obj: object):
        """`obj` should be a mapping."""

        obj = compile_mapping(obj)

        extraction_obj = obj.get(_KEY_DESCRIBE)
        with on_key(_KEY_DESCRIBE):
            extractor = self._extraction_compiler.compile(extraction_obj)

        predicate_objs = obj.get(_KEY_SHOULD, [])
        if not isinstance(predicate_objs, list):
            predicate_objs = [predicate_objs]
        with on_key(_KEY_SHOULD):
            predicates = list(map_compile(
                self._predicate_compiler.compile,
                predicate_objs,
            ))

        return AnalysisDescription(extractor=extractor, predicates=predicates)
