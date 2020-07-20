"""Verification."""

from preacher.core.extraction.analysis import (
    Analyzer,
    Analysis,
    analyze_json_str,
    analyze_xml_str,
    analyze_data_obj,
)
from preacher.core.extraction.extraction import (
    Extractor,
    JqExtractor,
    XPathExtractor,
    KeyExtractor,
    ExtractionError,
)
from .description import Description
from .matcher import Matcher, StaticMatcher, ValueMatcher, RecursiveMatcher
from .predicate import Predicate, MatcherPredicate
from .response import ResponseDescription, ResponseVerification
from .response_body import ResponseBodyDescription
from .type import require_type
from .verification import Verification, collect_verification

__all__ = [
    'Analyzer',
    'Analysis',
    'analyze_json_str',
    'analyze_xml_str',
    'analyze_data_obj',
    'Description',
    'Extractor',
    'JqExtractor',
    'XPathExtractor',
    'KeyExtractor',
    'ExtractionError',
    'Matcher',
    'StaticMatcher',
    'ValueMatcher',
    'RecursiveMatcher',
    'Predicate',
    'MatcherPredicate',
    'ResponseDescription',
    'ResponseVerification',
    'ResponseBodyDescription',
    'require_type',
    'Verification',
    'collect_verification',
]
