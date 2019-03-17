from flask import Flask, jsonify


APP = Flask(__name__)
APP.debug = True


@APP.route('/path/to/foo', methods=['GET'])
def foo() -> dict:
    return jsonify({'foo': 'bar'})


def main() -> None:
    APP.run('localhost')


if __name__ == '__main__':
    main()
