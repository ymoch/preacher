from datetime import datetime, timedelta, timezone
from functools import wraps
from time import sleep

import responder


api = responder.API()


@api.route('/json')
def json(req, res) -> None:
    res.media = {
        'foo': 'bar',
        'empty_string': '',
        'empty_list': [],
        'list': [1, 2, 'A'],
    }


@api.route('/xml')
def xml(req, res) -> None:
    res.headers['content-type'] = 'application/xml'
    res.text = (
'''<?xml version="1.0"?>
<root>
    <foo id="foo1">foo1-text</foo>
    <foo id="foo2">foo2-text</foo>
    <bar id="bar1">
        <baz id="baz1"/>
    </bar>
    <bar id="bar2">
        <baz id="baz2"/>
    </bar>
</root>
'''
    )    


@api.route('/later/{seconds}')
def now(req, res, *, seconds) -> None:
    dt = datetime.now(timezone.utc) + timedelta(seconds=int(seconds))
    res.media = {'now': dt.isoformat()}


@api.route('/text')
def text(req, res) -> None:
    res.text = 'text'


@api.route('/error/404')
def not_found(req, res) -> None:
    res.status_code = api.status_codes.HTTP_404
    res.media = {'message': 'not found'}


@api.route('/header')
def header(req, res) -> None:
    res.media = {key: value for (key, value) in req.headers.items()}


def main() -> None:
    api.run()


if __name__ == '__main__':
    main()
