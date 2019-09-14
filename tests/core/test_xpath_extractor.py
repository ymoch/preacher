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
))
def test_extract(query, expected, analyzer):
    extractor = XPathExtractor(query)
    actual = extractor.extract(analyzer)
    assert actual == expected
