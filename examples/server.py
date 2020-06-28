import zlib
import time
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, make_response, render_template, request


api = Flask(__name__)


@api.route('/json')
def json():
    return jsonify({
        'foo': 'bar',
        'empty_string': '',
        'empty_list': [],
        'list': [1, 2, 'A'],
        'items': [
            {'x': '1'},
            {},
            {'x': '2'},
        ],
    })


@api.route('/echo', methods=['GET', 'POST', 'PUT', 'DELETE'])
def echo():
    return jsonify({
        'method': request.method,
        'path': request.path,
        'headers': dict(request.headers.items()),
        'args': dict(request.args.lists()),
        'form': dict(request.form.lists()),
        'json': request.json,
    })


@api.route('/error/404')
def not_found():
    return jsonify({'message': 'not found'}), 404


@api.route('/xml')
def xml():
    res = make_response(render_template('sample.xml'))
    res.headers['content-type'] = 'application/xml'
    return res


@api.route('/later/<int:seconds>')
def later(seconds):
    dt = datetime.now(timezone.utc) + timedelta(seconds=int(seconds))
    return jsonify({'now': dt.isoformat()})


@api.route('/text')
def text():
    res = make_response('text')
    res.headers['content-type'] = 'text/plain'
    return res


@api.route('/binary')
def binary():
    res = make_response(zlib.compress(b'text'))
    res.headers['content-type'] = 'application/octet-stream'
    return res


@api.route('/sleep/<int:seconds>')
def sleep(seconds):
    time.sleep(float(seconds))

    res = make_response('OK')
    res.headers['content-type'] = 'text/plain'
    return res


def main() -> None:
    api.run()


if __name__ == '__main__':
    main()
