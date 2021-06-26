from click import Option

from preacher.app.cli.executor import PROCESS_POOL_FACTORY, THREAD_POOL_FACTORY
from preacher.app.cli.option import LevelType, ExecutorFactoryType
from preacher.core.status import Status


def test_level_type():
    tp = LevelType()

    param = Option(["--level"])
    assert tp.get_metavar(param) == "[skipped|success|unstable|failure]"
    assert tp.get_missing_message(param) == (
        "Choose from:\n\tskipped,\n\tsuccess,\n\tunstable,\n\tfailure"
    )

    assert tp.convert("skipped", None, None) == Status.SKIPPED
    assert tp.convert("SUCCESS", None, None) == Status.SUCCESS
    assert tp.convert("UnStable", None, None) == Status.UNSTABLE
    assert tp.convert("FAILURE", None, None) == Status.FAILURE
    assert tp.convert(Status.SUCCESS, None, None) == Status.SUCCESS


def test_executor_factory_type():
    tp = ExecutorFactoryType()

    param = Option(["--executor"])
    assert tp.get_metavar(param) == "[process|thread]"
    assert tp.get_missing_message(param) == "Choose from:\n\tprocess,\n\tthread"

    assert tp.convert("process", None, None) is PROCESS_POOL_FACTORY
    assert tp.convert("Thread", None, None) is THREAD_POOL_FACTORY
    assert tp.convert(PROCESS_POOL_FACTORY, None, None) is PROCESS_POOL_FACTORY
