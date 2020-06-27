from pytest import raises

from preacher.compilation.request_body import RequestBodyCompiled


def test_fix():
    compiled = RequestBodyCompiled()
    with raises(NotImplementedError):
        compiled.fix()
