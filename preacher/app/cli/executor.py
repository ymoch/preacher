from abc import ABC, abstractmethod
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor


class ExecutorFactory(ABC):
    """
    Executor factory interface.
    """

    @abstractmethod
    def create(self, concurrency: int) -> Executor:
        """Create an executor."""


class _ProcessPoolFactory(ExecutorFactory):
    def create(self, concurrency: int) -> Executor:
        return ProcessPoolExecutor(concurrency)


class _ThreadPoolFactory(ExecutorFactory):
    def create(self, concurrency: int) -> Executor:
        return ThreadPoolExecutor(concurrency)


PROCESS_POOL_FACTORY = _ProcessPoolFactory()
THREAD_POOL_FACTORY = _ThreadPoolFactory()
