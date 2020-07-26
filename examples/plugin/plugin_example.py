"""
Custom matchers example.
- according to: https://pyhamcrest.readthedocs.io/en/stable/custom_matchers/
"""

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description

from preacher.compilation.verification import MatcherFactoryCompiler
from preacher.plugin import hookimpl


class IsEven(BaseMatcher[int]):

    def _matches(self, item: int) -> bool:
        return item % 2 == 0

    def describe_to(self, description: Description) -> None:
        description.append_text('even')


class IsMultipleOf(BaseMatcher[int]):

    def __init__(self, base: int):
        self.base = base

    def _matches(self, item: int) -> bool:
        return item % self.base == 0

    def describe_to(self, description: Description) -> None:
        description.append_text('multiple of ').append_description_of(self.base)


@hookimpl
def preacher_add_matchers(compiler: MatcherFactoryCompiler) -> None:
    """
    An example of adding matchers.
    """

    # Add a static matcher.
    compiler.add_static(('be_even', 'is_even', 'even'), IsEven())

    # Add a matcher taking a value.
    compiler.add_taking_value(('be_multiple_of', 'is_multiple_of', 'multiple_of'), IsMultipleOf)
