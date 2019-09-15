from datetime import datetime, timezone
from functools import wraps
from time import sleep

import responder


api = responder.API()


def pre_latency(seconds):
    def _latency(func):
        @wraps(func)
        def _latency_func(*args, **kwargs):
            sleep(seconds)
            return func(*args, **kwargs)
        return _latency_func
    return _latency


@api.route('/json')
@pre_latency(1.0)
def json(req, res) -> None:
    res.media = {
        'foo': 'bar',
        'empty_string': '',
        'empty_list': [],
        'list': [1, 2, 'A'],
        'now': datetime.now(timezone.utc).isoformat(),
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
