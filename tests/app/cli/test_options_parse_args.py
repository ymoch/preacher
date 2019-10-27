from pytest import mark, raises

from preacher.app.cli.option import parse_args


@mark.parametrize('args', [
    ["-h"],
    ["--help"],
    ["-v"],
    ["--version"],
])
def test_show_and_exit(args):
    with raises(SystemExit) as ex_info:
        parse_args(["-v"])
    assert ex_info.value.code == 0
