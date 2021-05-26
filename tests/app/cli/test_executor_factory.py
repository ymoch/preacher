from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from preacher.app.cli.executor import PROCESS_POOL_FACTORY, THREAD_POOL_FACTORY


def test_process_pool_factory():
    executor = PROCESS_POOL_FACTORY.create(1)
    assert isinstance(executor, ProcessPoolExecutor)


def test_thread_pool_factory():
    executor = THREAD_POOL_FACTORY.create(1)
    assert isinstance(executor, ThreadPoolExecutor)
