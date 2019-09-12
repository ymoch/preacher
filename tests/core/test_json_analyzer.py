from unittest.mock import MagicMock

from preacher.core.analysis import analyze_json_str


def test_analyze_with_jq():
    analyzer = analyze_json_str('{"k1":"v1","k2":"v2"}')
    extract = MagicMock(return_value='value')
    value = analyzer.jq(extract)
    assert value == 'value'

    extract.assert_called_once_with({'k1': 'v1', 'k2': 'v2'})
