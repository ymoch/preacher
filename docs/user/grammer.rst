Grammer
=======

Scenario
--------
A ``Scenario`` is written in `YAML`_.
A ``Scenario`` is a mapping that consists of below:

- label: ``String`` (Recommended)
    - A label of this scenario.
    - This field is actually optional but recommended to tell this scenario from another.
- default: ``Default`` (Optional)
    - Default of this scenario.
- cases: ``List<Case>``
    - Test cases.

Case
----
A ``Case`` is a mapping that consists of below:

- label: ``String`` (Recommended)
    - A label of this case.
    - This field is actually optional but recommended to tell this case from another.
- request: ``Request`` (Optional)
    - A request.
- response: ``ResponseDescription`` (Optional)
    - A response description.

Request
-------
A ``Request`` is a mapping or a string.

A mapping for ``Request`` has items below:

- path: ``String`` (Optional)
    - A request path. The default value is ``''``.
- Headers: ``Mapping<String, String>`` (Optional)
    - Request headers as a mapping of names to values.
- params: ``Mapping<String, String>`` (Optional)
    - Query parameters as a mapping of keys to values.

When given a string, that is equivalent to ``{"path": it}``.

Response Decription
-------------------
A ``ResponseDescription`` is a mapping that consists of below:

- status_code: ``Integer``, ``Predicate`` or ``List<Predicate>`` (Optional)
    - Predicates that match a status code as an integer value.
    - When given a number, that is equivalent to ``{"equal": it}``.
- headers:
    - Descriptions that descript the response headers.
    - Response headers are validated as a mapping of names to values
      and can be descripted by `jq_` query (e.g. ``."content-type"``).
      *Note that Names are lower-cased* to normalize.
- body: ``BodyDescription`` (Optional)
    - A description that descript the response body.

Body Description
----------------
A ``BodyDescription`` is a mapping or a list.

A mapping for ``BodyDescription`` has items below.

- analyzed_as: ``String`` (Optional)
    - The method to analyze the body. The default value is ``json``.
    - When given ``json``, the body is analyzed as a JSON.
    - When given ``xml``, the body is analyzed as an XML.
- descriptions: ``Description`` or ``List<Description>``
    - Descriptions that descript the response body.

When given a list, that is equivalent to ``{"descritptions": it}``.

Description
-----------
A ``Description`` is a mapping that consists of below:

- describe: ``Extraction``
    - An extraction process.
- should: ``Predicate``, or ``List<Predicate>>`` (Optional)
    - Predicates that match the descripted value.

Extraction
----------
An Extraction is a mapping or a string.

A mapping for Extraction has one of below:

- jq: ``String``
    - A `jq`_ query.
- xpath: ``String``
    - A `XPath`_ query
- multiple: ``Boolean`` (Optional)
    - When given ``true``, it returns the list of all extracted values.
    - When given ``false``, it returns the first of extracted values.
    - The default value is ``false``.
- cast_to: ``String`` (Optional)
    - When given, it returns the casted value.
    - Allowed values are ``int``, ``float``, ``string``.
    - Casting does not affect ``null``.

When given a string, that is equivalent to {"jq": it}.

.. note:: The extraction must be compatible for the body analysis.

   +----------------------------+----+-------+
   | Body Analysis / Extraction | jq | xpath |
   +============================+====+=======+
   | JSON                       |  o |     x |
   +----------------------------+----+-------+
   | XML                        |  x |     o |
   +----------------------------+----+-------+

Predicate
---------
A ``Predicate`` is a ``Matcher`` (can be extended in the future).

Matcher
-------
A ``Matcher`` is a string or a mapping that has an item.
Allowed matchers are below.

.. note:: A matchers taking ``none`` is given as a string like ``{"should": "be_null"}``.
.. note:: A ``Value`` given as a ``Matcher`` is equivalent to ``{"equal": it}``.

Object
^^^^^^
- be: ``Matcher``
    - Matches the given matcher.
- be_null: ``none``
    - Matches if it is a null value.
- not_be_null: ``none``
    - Matches if it is not a null value.
- equal: ``Value``
    - Matches if it equals the given value.
- have_length: ``Integer``
    - Matches if it has a length and its length is equal to the given value.

Comparable
^^^^^^^^^^
- be_greater_than: ``Comparable``
    - Matches if it is greater than the given value (it > argument).
- be_greater_than_or_equal_to: ``Comparable``
    - Matches if it is greater than or equal to the given value (it >= argument).
- be_less_than: ``Comparable``
    - Matches if it is less than the given value (it < argument).
- be_less_than_or_equal_to: ``Comparable``
    - Matches if it is less than or equal to the given value (it < argument).

String
^^^^^^
- contain_string: ``String``
    - Matches if it is an string and contains the given value.
- start_with: ``String``
    - Matches if it is an string and starts with the given value.
- end_with: ``String``
    - Matches if it is an string and ends with the given value.
- match_regexp: ``String``
    - Matches if it is an string and matches the given regular expression.

Datetime
^^^^^^^^
- be_before: ``String``
    - Matches if it is a datetime and before the given datetime.
    - When given ``now``, then compares to the datetime just when the request starts.
    - When given an offset, then compares to the datetime when the request starts.
        - Days, hours, minutes and seconds offsets are available.
        - When given a positive offset like ``1 day`` or ``+2 hours``,
          then compares to the future datetime.
        - When given a negative offset like ``-1 minute`` or ``-2 seconds``,
          then compares to the past datetime.
- be_after: ``String``
    - Matches if it is a datetime and after the given datetime.
    - Usage is the same as ``be_before``.

.. note:: Validated datetime values must be in ISO 8601 format
          like ``2019-01-23T12:34:56Z``.

Sequence
^^^^^^^^
- be_empty: ``none``
    - Matches an empty sequence.
- have_item: ``Matcher``
    - Matches if it is a collection and has the given item.
- have_items: ``List<Matcher>``
    - Matches if all given items appear in the list, in any order.
- contain: ``List<Matcher>``
    - Exactly matches the entire sequence.
- contain_in_any_order: ``List<Matcher>``
    - Matches the entire sequence, but in any order.

Logical
^^^^^^^
- not: ``Matcher``
    - Matches if it doesn't match the given matcher.
- all_of: ``List<Matcher>``
    - Matches if it matches all of the given matchers.
- any_of: ``List<Matcher>``
    - Matches if it matches any of the given matchers.
- anything: ``none``
    - Matches anything.

Default
-------
A ``Default`` is a mapping that consists of below:

- request: ``Request`` (Optional)
    - A request to overwrite the default request values.
- response: ``ResponseDescription`` (Optional)
    - A response description to overwrite the default response description values.

.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _XPATH: https://www.w3.org/TR/xpath/all/
