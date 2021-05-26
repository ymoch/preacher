from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

from click import Command, Context, Option

from preacher.app.cli.option import LevelType, ExecutorFactoryType
from preacher.core.status import Status


def test_level_type():
    tp = LevelType()

    param = Option(['--level'])
    assert tp.get_metavar(param) == '[skipped|success|unstable|failure]'
    assert tp.get_missing_message(param) == (
        'Choose from:\n\tskipped,\n\tsuccess,\n\tunstable,\n\tfailure'
    )

    context = Context(Command('preacher-cli'))
    assert tp.convert('skipped', None, context) == Status.SKIPPED
    assert tp.convert('SUCCESS', None, context) == Status.SUCCESS
    assert tp.convert('UnStable', None, context) == Status.UNSTABLE
    assert tp.convert('FAILURE', None, context) == Status.FAILURE


def test_executor_factory_type():
    tp = ExecutorFactoryType()

    param = Option(['--executor'])
    assert tp.get_metavar(param) == '[process|thread]'
    assert tp.get_missing_message(param) == 'Choose from:\n\tprocess,\n\tthread'

    context = Context(Command('preacher-cli'))
    assert tp.convert('process', None, context) is ProcessPoolExecutor
    assert tp.convert('Thread', None, context) is ThreadPoolExecutor
