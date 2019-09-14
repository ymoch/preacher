from pytest import fixture, mark

from preacher.core.analysis import Analyzer, analyze_xml_str
from preacher.core.extraction import XPathExtractor


XML_VALUE = '''
<html>
    <foo id="foo1">foo-text</foo>
    <foo id="foo2">
        <bar>text</bar>
        <baz attr="baz-attr" />
    </foo>
</html>
'''


@fixture
def analyzer() -> Analyzer:
    return analyze_xml_str(XML_VALUE)


@mark.parametrize('query, expected', (
    ('.//foo[1]', 'foo-text'),
    ('.//foo[@id="foo1"]', 'foo-text'),
    ('.//foo[2]/bar', 'text'),
    ('.//foo/baz/@attr', 'baz-attr'),
))
def test_extract(query, expected, analyzer):
    extractor = XPathExtractor(query)
    actual = extractor.extract(analyzer)
    assert actual == expected
