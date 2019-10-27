import os
import zlib
from datetime import datetime, timedelta, timezone

import responder


api = responder.API(
    static_dir=os.path.join(os.path.dirname(__file__), 'static'),
    templates_dir=os.path.join(os.path.dirname(__file__), 'templates'),
)


@api.route('/header')
def header(req, res) -> None:
    res.media = {key: value for (key, value) in req.headers.items()}


@api.route('/params')
def query_params(req, res) -> None:
    res.media = {key: value for (key, value) in req.params.items()}
    print(res.media)


@api.route('/error/404')
def not_found(req, res) -> None:
    res.status_code = api.status_codes.HTTP_404
    res.media = {'message': 'not found'}


@api.route('/json')
def json(req, res) -> None:
    res.media = {
        'foo': 'bar',
        'empty_string': '',
        'empty_list': [],
        'list': [1, 2, 'A'],
        'items': [
            {'x': '1'},
            {},
            {'x': '2'},
        ],
    }


@api.route('/xml')
def xml(req, res) -> None:
    res.headers['content-type'] = 'application/xml'
    res.content = api.template('sample.xml')


@api.route('/later/{seconds}')
def now(req, res, *, seconds) -> None:
    dt = datetime.now(timezone.utc) + timedelta(seconds=int(seconds))
    res.media = {'now': dt.isoformat()}


@api.route('/text')
def text(req, res) -> None:
    res.text = 'text'


@api.route('/binary')
def binary(req, res) -> None:
    res.headers['content-type'] = 'application/octet-stream'
    res.content = zlib.compress(b'text')


def main() -> None:
    api.run()


if __name__ == '__main__':
    main()
