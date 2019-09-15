import os
from datetime import datetime, timedelta, timezone

import responder


api = responder.API(
    static_dir=None,
    templates_dir=os.path.join(os.path.dirname(__file__), 'templates'),
)


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
    res.text = api.template('sample.xml')


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
