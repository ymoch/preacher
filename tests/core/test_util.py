import time
from unittest.mock import MagicMock, patch

from preacher.core.util import now


@patch('time.localtime')
def test_now_jst(localtime):
    localtime.return_value = MagicMock(
        spec=time.struct_time,
        tm_zone='JST',
        tm_gmtoff=32400,
    )
    current = now()
    assert current.tzname() == 'JST'
    assert current.utcoffset().total_seconds() == 32400


@patch('time.localtime')
def test_now_pdt(localtime):
    localtime.return_value = MagicMock(
        spec=time.struct_time,
        tm_zone='PDT',
        tm_gmtoff=-28800,
    )
    current = now()
    assert current.tzname() == 'PDT'
    assert current.utcoffset().total_seconds() == -28800
