from flask import Flask, abort, jsonify


app = Flask(__name__)
app.debug = True


@app.route('/text', methods=['GET'])
def text() -> str:
    return 'text'


@app.route('/json', methods=['GET'])
def foo() -> dict:
    return jsonify({
        'foo': 'bar',
        'empty_string': '',
        'empty_list': [],
    })


@app.route('/error/404', methods=['GET'])
def not_found() -> None:
    return abort(404, {'message': 'not found'})


def main() -> None:
    app.run('localhost')


if __name__ == '__main__':
    main()
