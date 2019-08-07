from functools import wraps
from time import sleep

from flask import Flask, abort, jsonify


app = Flask(__name__)
app.debug = True


def latency(seconds):
    def _latency(func):
        @wraps(func)
        def _latency_func(*args, **kwargs):
            sleep(seconds)
            return func(*args, **kwargs)
        return _latency_func
    return _latency


@app.route('/text', methods=['GET'])
@latency(1.0)
def text():
    return 'text'


@app.route('/json', methods=['GET'])
def foo():
    return jsonify({
        'foo': 'bar',
        'empty_string': '',
        'empty_list': [],
        'list': [1, 2, 'A'],
    })


@app.route('/error/404', methods=['GET'])
def not_found():
    return abort(404, {'message': 'not found'})


def main() -> None:
    app.run('localhost')


if __name__ == '__main__':
    main()
