"""Description compilation."""

from preacher.compilation.error import on_key
from preacher.compilation.extraction import ExtractionCompiler
from preacher.compilation.util.functional import map_compile
from preacher.compilation.util.type import ensure_list, ensure_mapping, ensure_optional_str
from preacher.core.verification import Description
from .predicate import PredicateCompiler

_KEY_DESCRIBE = "describe"
_KEY_SHOULD = "should"
_KEY_AS = "as"


class DescriptionCompiler:
    def __init__(self, extraction: ExtractionCompiler, predicate: PredicateCompiler):
        self._extraction = extraction
        self._predicate = predicate

    def compile(self, obj: object):
        """`obj` should be a mapping."""

        obj = ensure_mapping(obj)

        extraction_obj = obj.get(_KEY_DESCRIBE)
        with on_key(_KEY_DESCRIBE):
            extractor = self._extraction.compile(extraction_obj)

        predicate_objs = ensure_list(obj.get(_KEY_SHOULD, []))
        with on_key(_KEY_SHOULD):
            predicates = list(
                map_compile(
                    self._predicate.compile,
                    predicate_objs,
                )
            )

        value_name_obj = obj.get(_KEY_AS)
        with on_key(_KEY_AS):
            value_name = ensure_optional_str(value_name_obj)

        return Description(extractor=extractor, predicates=predicates, value_name=value_name)
