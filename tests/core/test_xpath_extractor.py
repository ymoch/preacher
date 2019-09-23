from unittest.mock import MagicMock

from lxml.etree import XMLParser, fromstring
from pytest import fixture, mark

from preacher.core.extraction import XPathExtractor


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
    return MagicMock(
        xpath=MagicMock(side_effect=lambda x: x(elem))
    )


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
    assert not extractor.multiple

    actual = extractor.extract(analyzer)
    assert actual == expected


@mark.parametrize('query, multiple, cast, expected', (
    ('/root/xxx', False, None, None),
    ('/root/foo', False, None, 'foo-text'),
    ('./foo[1]', False, None, 'foo-text'),
    ('//foo[@id="foo1"]', False, None, 'foo-text'),
    ('.//foo[2]/bar', False, None, 'text'),
    ('//baz/@attr', False, None, 'baz-attr'),
    ('/root/xxx', True, None, None),
    ('/root/foo', True, None, ['foo-text', '\n        ']),
    ('./foo/bar', True, None, ['text']),
    ('./foo/bar', True, None, ['text']),
    ('./number', False, None, '10'),
    ('./number', False, int, 10),
    ('./numbers/value', True, None, ['1', '2']),
    ('./numbers/value', True, int, [1, 2]),
))
def test_extract(query, multiple, cast, expected, analyzer):
    extractor = XPathExtractor(query, multiple=multiple, cast=cast)
    assert extractor.multiple == multiple

    actual = extractor.extract(analyzer)
    assert actual == expected
