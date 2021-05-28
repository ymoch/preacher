Matcher
=======
A matcher taking no argument is given as a string such like ``"be_null"``.
A matcher taking an argument is given as a dictionary such like ``equal: 1``.

A ``Value`` given as a ``Matcher`` is equivalent to ``equal: it``.

For Objects
-----------
.. list-table:: Matchers for Objects
    :header-rows: 1
    :widths: 20 20 60

    * - Name
      - Arguments
      - Description
    * - be
      - none
      - Matches an object that matches the given matcher.
    * - be_null
      - none
      - Matches ``null``.
    * - not_be_null
      - none
      - Matches not ``null``.
    * - equal
      - ``Value``
      - Matches an equal object
    * - have_length
      - ``Integer``
      - Matches an object that has a length and whose length matches the given matcher.

For Comparable Values
---------------------
.. list-table:: Matchers for Comparable Values
    :header-rows: 1
    :widths: 20 20 60

    * - Name
      - Arguments
      - Description
    * - be_greater_than
      - ``Comparable``
      - Matches a value that is greater than the given value ``(it > argument)``.
    * - be_greater_than_or_equal_to
      - ``Comparable``
      - Matches a value that is greater than or equal to the given value ``(it >= argument)``.
    * - be_less_than
      - ``Comparable``
      - Matches a value that is less than the given value ``(it < argument)``.
    * - be_less_than_or_equal_to
      - ``Comparable``
      - Matches a value that is less than or equal to the given value ``(it <= argument)``.

For String Values
-----------------
.. list-table:: Matchers for String Values
    :header-rows: 1
    :widths: 20 20 60

    * - Name
      - Arguments
      - Description
    * - contain_string
      - ``String``
      - Matches a string that contains the given string.
    * - start_with
      - ``String``
      - Matches a string that starts with the given string.
    * - end_with
      - ``String``
      - Matches a string that ends with the given string.
    * - match_regexp
      - ``String``
      - Matches a string that matches the given regular expression.

For Datetime Values
-------------------
.. note:: Validated datetime values must be in ISO 8601 format
          like ``2019-01-23T12:34:56Z``.

.. list-table:: Matchers for Datetime Values
    :header-rows: 1
    :widths: 20 20 60

    * - Name
      - Arguments
      - Description
    * - be_monday
      - none
      - Matches a datetime on Monday.
    * - be_tuesday
      - none
      - Matches a datetime on Tuesday.
    * - be_wednesday
      - none
      - Matches a datetime on Wednesday.
    * - be_thursday
      - none
      - Matches a datetime on Thursday.
    * - be_friday
      - none
      - Matches a datetime on Friday.
    * - be_saturday
      - none
      - Matches a datetime on Saturday.
    * - be_sunday
      - none
      - Matches a datetime on Sunday.
    * - be_before
      - :ref:`datetime`
      - Matches a datetime before the given datetime.
    * - be_after
      - :ref:`datetime`
      - Matches a datetime after the given datetime.

.. _datetime:

Datetime
^^^^^^^^
An "absolute datetime" is given as a YAML timestamp value.
A naive datetime value is regarded as a UTC datetime.

A "relative datetime" is given as a string value in the particular format.

- When given ``now``, then uses the datetime just when the request starts.
- When given time such like ``12:34+0100``,
  then uses the datetime which is the combination of
  date that the requests starts and the given time.
- When given an offset, then uses the datetime that the request starts.
    - Days, hours, minutes and seconds offsets are available.
    - When given a positive offset like ``1 day`` or ``+2 hours``,
      then uses the future datetime.
    - When given a negative offset like ``-1 minute`` or ``-2 seconds``,
      then uses the past datetime.

For Sequence Values
-------------------
.. list-table:: Matchers for Sequence Values
    :header-rows: 1
    :widths: 20 20 60

    * - Name
      - Arguments
      - Description
    * - be_empty
      - none
      - Matches an empty sequence.
    * - have_item
      - ``Matcher``
      - Matches a collection that has an item matching the given item.
    * - have_items
      - ``List<Matcher>``
      - Matches if all given items appear in the list, in any order.
    * - contain_exactly
      - ``List<Matcher>``
      - Exactly matches the entire sequence.
    * - contain_in_any_order
      - ``List<Matcher>``
      - Matches the entire sequence, but in any order.

Logical Matchers
----------------
.. list-table:: Logical Matchers
    :header-rows: 1
    :widths: 20 20 60

    * - Name
      - Arguments
      - Description
    * - not
      - ``Matcher``
      - Matches a value that doesn't match the given matcher.
    * - all_of
      - ``List<Matcher>``
      - Matches a value that matches all of the given matchers.
    * - any_of
      - ``List<Matcher>``
      - Matches a value that matches any of the given matchers.
    * - anything
      - none
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
