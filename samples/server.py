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


@api.route('/text')
def text(req, res) -> None:
    res.text = 'text'


@api.route('/json')
@pre_latency(1.0)
def foo(req, res) -> None:
    res.media = {
        'foo': 'bar',
        'empty_string': '',
        'empty_list': [],
        'list': [1, 2, 'A'],
        'now': datetime.now(timezone.utc).isoformat(),
    }


@api.route('/error/404')
def not_found(req, res) -> None:
    res.status_code = api.status_codes.HTTP_404
    res.media = {'message': 'not found'}


def main() -> None:
    api.run()


if __name__ == '__main__':
    main()
