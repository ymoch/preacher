from unittest.mock import Mock, NonCallableMock

from lxml.etree import XMLParser, fromstring
from pytest import fixture, mark, raises

from preacher.core.functional import identify
from preacher.core.scenario import Analyzer
from preacher.core.scenario.extraction import XPathExtractor, ExtractionError

VALUE = '''
<root>
    <foo id="foo1">foo-text</foo>
    <foo id="foo2">
        <bar>text</bar>
        <baz attr="baz-attr" />
    </foo>
    <number>10</number>
    <numbers>
        <value>1</value>
    </numbers>
    <numbers>
    </numbers>
    <numbers>
        <value>2</value>
    </numbers>
</root>
'''


@fixture
def analyzer():
    elem = fromstring(VALUE, parser=XMLParser())
    return NonCallableMock(Analyzer, xpath=Mock(side_effect=lambda x: x(elem)))


def test_extract_invalid(analyzer):
    extractor = XPathExtractor('.items')
    with raises(ExtractionError) as error_info:
        extractor.extract(analyzer)
    assert str(error_info.value).endswith(': .items')


@mark.parametrize('query, expected', (
    ('/root/xxx', None),
    ('/root/foo', 'foo-text'),
    ('./foo[1]', 'foo-text'),
    ('//foo[@id="foo1"]', 'foo-text'),
    ('.//foo[2]/bar', 'text'),
    ('//baz/@attr', 'baz-attr'),
    ('./number', '10'),
    ('./numbers/value', '1'),
))
def test_extract_default(query, expected, analyzer):
    extractor = XPathExtractor(query)
    assert extractor.extract(analyzer) == expected


@mark.parametrize('query, multiple, cast, expected', (
    ('/root/xxx', False, identify, None),
    ('/root/foo', False, identify, 'foo-text'),
    ('./foo[1]', False, identify, 'foo-text'),
    ('//foo[@id="foo1"]', False, identify, 'foo-text'),
    ('.//foo[2]/bar', False, identify, 'text'),
    ('//baz/@attr', False, identify, 'baz-attr'),
    ('/root/xxx', True, identify, None),
    ('/root/foo', True, identify, ['foo-text', '\n        ']),
    ('./foo/bar', True, identify, ['text']),
    ('./foo/bar', True, identify, ['text']),
    ('./number', False, identify, '10'),
    ('./number', False, int, 10),
    ('./numbers/value', True, identify, ['1', '2']),
    ('./numbers/value', True, int, [1, 2]),
))
def test_extract(query, multiple, cast, expected, analyzer):
    extractor = XPathExtractor(query, multiple=multiple, cast=cast)
    assert extractor.extract(analyzer) == expected
