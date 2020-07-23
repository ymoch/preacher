from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

from preacher.app.cli.option import LevelType, ExecutorFactoryType
from preacher.core.status import Status


def test_level_type():
    tp = LevelType()
    assert tp.get_metavar(None) == '[skipped|success|unstable|failure]'
    assert tp.get_missing_message(None) == (
        'Choose from:\n\tskipped,\n\tsuccess,\n\tunstable,\n\tfailure.'
    )
    assert tp.convert('skipped', None, None) == Status.SKIPPED
    assert tp.convert('SUCCESS', None, None) == Status.SUCCESS
    assert tp.convert('UnStable', None, None) == Status.UNSTABLE
    assert tp.convert('FAILURE', None, None) == Status.FAILURE


def test_executor_factory_type():
    tp = ExecutorFactoryType()
    assert tp.get_metavar(None) == '[process|thread]'
    assert tp.get_missing_message(None) == (
        'Choose from:\n\tprocess,\n\tthread.'
    )
    assert tp.convert('process', None, None) is ProcessPoolExecutor
    assert tp.convert('Thread', None, None) is ThreadPoolExecutor
