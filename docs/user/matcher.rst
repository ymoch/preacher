Matcher
=======
A ``Matcher`` is a string or a mapping that has an item.
Allowed matchers are below.

.. note:: A ``Value`` given as a ``Matcher`` is equivalent to ``{"equal": it}``.

For Objects
-----------
- be: ``Matcher``
    - Matches the given matcher.
- be_null
    - Matches if it is a null value.
- not_be_null
    - Matches if it is not a null value.
- equal: ``Value``
    - Matches if it equals the given value.
- have_length: ``Integer``
    - Matches if it has a length and its length is equal to the given value.

For Comparable Values
---------------------
- be_greater_than: ``Comparable``
    - Matches if it is greater than the given value (it > argument).
- be_greater_than_or_equal_to: ``Comparable``
    - Matches if it is greater than or equal to the given value (it >= argument).
- be_less_than: ``Comparable``
    - Matches if it is less than the given value (it < argument).
- be_less_than_or_equal_to: ``Comparable``
    - Matches if it is less than or equal to the given value (it < argument).

For String Values
-----------------
- contain_string: ``String``
    - Matches if it is an string and contains the given value.
- start_with: ``String``
    - Matches if it is an string and starts with the given value.
- end_with: ``String``
    - Matches if it is an string and ends with the given value.
- match_regexp: ``String``
    - Matches if it is an string and matches the given regular expression.

For Datetime Values
-------------------
- be_before: :ref:`datetime`
    - Matches if it is a datetime and before the given datetime.
- be_after: ``String``
    - Matches if it is a datetime and after the given datetime.
    - Usage is the same as ``be_before``.

.. _datetime:

Datetime
^^^^^^^^
An "absolute datetime" is given as a YAML timestamp value.
A naive datetime value is regarded as a UTC datetime.

A "relative datetime" is given as a string value in the particular format.

- When given ``now``, then compares to the datetime just when the request starts.
- When given an offset, then compares to the datetime when the request starts.
    - Days, hours, minutes and seconds offsets are available.
    - When given a positive offset like ``1 day`` or ``+2 hours``,
      then compares to the future datetime.
    - When given a negative offset like ``-1 minute`` or ``-2 seconds``,
      then compares to the past datetime.

.. note:: Validated datetime values must be in ISO 8601 format
          like ``2019-01-23T12:34:56Z``.

For Sequence values
-------------------
- be_empty
    - Matches an empty sequence.
- have_item: ``Matcher``
    - Matches if it is a collection and has the given item.
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
    - Matches if it doesn't match the given matcher.
- all_of: ``List<Matcher>``
    - Matches if it matches all of the given matchers.
- any_of: ``List<Matcher>``
    - Matches if it matches any of the given matchers.
- anything
    - Matches anything.
