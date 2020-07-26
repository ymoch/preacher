Matcher
=======
A string or a dictionary is given as a ``Matcher``. Allowed matchers are below.

.. note:: A ``Value`` given as a ``Matcher`` is equivalent to ``{"equal": it}``.

For Objects
-----------
- be: ``Matcher``
    - Matches an object that matches the given matcher.
- be_null
    - Matches ``null``.
- not_be_null
    - Matches not ``null``.
- equal: ``Value``
    - Matches an equal object.
- have_length: ``Integer``
    - Matches an object that has a length and whose length matches the given matcher.

For Comparable Values
---------------------
- be_greater_than: ``Comparable``
    - Matches a value that is greater than the given value (it > argument).
- be_greater_than_or_equal_to: ``Comparable``
    - Matches a value that is greater than or equal to the given value (it >= argument).
- be_less_than: ``Comparable``
    - Matches a value that is less than the given value (it < argument).
- be_less_than_or_equal_to: ``Comparable``
    - Matches a value that is less than or equal to the given value (it < argument).

For String Values
-----------------
- contain_string: ``String``
    - Matches an string that contains the given string.
- start_with: ``String``
    - Matches an string that starts with the given string.
- end_with: ``String``
    - Matches an string that ends with the given string.
- match_regexp: ``String``
    - Matches an string that matches the given regular expression.

For Datetime Values
-------------------
- be_before: :ref:`datetime`
    - Matches a datetime before the given datetime.
- be_after: :ref:`datetime`
    - Matches a datetime after the given datetime.

.. note:: Validated datetime values must be in ISO 8601 format
          like ``2019-01-23T12:34:56Z``.

.. _datetime:

Datetime
^^^^^^^^
An "absolute datetime" is given as a YAML timestamp value.
A naive datetime value is regarded as a UTC datetime.

A "relative datetime" is given as a string value in the particular format.

- When given ``now``, then uses the datetime just when the request starts.
- When given an offset, then uses the datetime before or after the request starts.
    - Days, hours, minutes and seconds offsets are available.
    - When given a positive offset like ``1 day`` or ``+2 hours``,
      then uses the future datetime.
    - When given a negative offset like ``-1 minute`` or ``-2 seconds``,
      then uses the past datetime.

For Sequence values
-------------------
- be_empty
    - Matches an empty sequence.
- have_item: ``Matcher``
    - Matches a collection that has an item that matches the given item.
- have_items: ``List<Matcher>``
    - Matches if all given items appear in the list, in any order.
- contain_exactly: ``List<Matcher>``
    - Exactly matches the entire sequence.
- contain: ``List<Matcher>`` (Deprecated)
    - Same as ``contain_exactly``. ``contain`` will be removed in the future.
- contain_in_any_order: ``List<Matcher>``
    - Matches the entire sequence, but in any order.

Logical Matchers
----------------
- not: ``Matcher``
    - Matches a value that doesn't match the given matcher.
- all_of: ``List<Matcher>``
    - Matches a value that matches all of the given matchers.
- any_of: ``List<Matcher>``
    - Matches a value that matches any of the given matchers.
- anything
    - Matches anything.

Custom matchers
---------------
You can define custom matchers and load as a plugins.

First, implement a custom matcher plugin like below.

.. literalinclude:: /../examples/plugin/custom_matcher.py

And then, run Preacher with loading that plugin.

.. code-block:: sh

    $ preacher-cli -p path/to/plugin.py with-custom-matchers.yml

.. code-block:: yaml

    # with-custom-matchers.yml

    label: Custom matchers example
    response:
      body:
        describe: .six
        should:
          - be_even
          - be_multiple_of: 3
