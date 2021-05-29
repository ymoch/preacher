YAML Tag
========

``!include``: Including other YAML files
----------------------------------------
Using ``!include`` tag, you can include other YAML files.
This tag is available anywhere in your scenario.

.. code-block:: yaml

    !include path/to/other.yaml

A good practice of this feature is locating subscenarios on subdirectories.

.. code-block:: yaml

    label: Subscenario inclusion example
    subscenarios:
      - !include subscenarios/subscenario1.yml
      - !include subscenarios/subscenario2.yml

UNIX-like wildcard expansion is available.
A wildcard inclusion results in the list of matching inclusion.

.. code-block:: yaml

    !include path/to/*.yml

.. note:: Anchors in a included YAML are not available in including YAMLs,
          because the included YAMLs are parsed after the including YAML is parsed.

.. note:: Names of included files should not contain any wildcard characters
          because not all of the wildcard expansion rules are covered.

``!relative_datetime``: Give a relative datetime value with a format
--------------------------------------------------------------------
Using ``!relative_datetime`` tag, you can give a datetime with a format
relating to the executing datetime.

.. code-block:: yaml

    !relative_datetime
      delta: -60 seconds
      format: "%Y-%m-%d %H:%m:%s"

.. list-table:: The Definition of Relative Datetime
    :header-rows: 1
    :widths: 10 20 15 50

    * - Key
      - Type
      - Default
      - Description
    * - delta
      - :ref:`duration`
      - ``now``
      - The duration from the origin to the desired datetime.
    * - format
      - :ref:`datetime-format`
      - ``iso8601``
      - The datetime format,
        Which is used not only to dump a datetime value
        but also to parse the compared datetime value.

When simply given as a string, the value is regarded as ``delta``.

.. code-block:: yaml

    # These expressions have the same meaning.
    - !relative_datetime 3 days
    - !relative_datetime
        delta: 3 days

.. _duration:

Duration
^^^^^^^^
A ``Duration`` is given as a string value in the particular format.

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

.. note::

    A ``Duration`` can also be an absolute datetime
    to be compatible with matcher arguments such like ``be_before``.

.. _datetime-format:

Timestamp Format
^^^^^^^^^^^^^^^^
- When given ``iso8601``, then the format is an `ISO 8601`_ format.
- When given another string, then the format is regarded as a format string in `format codes`_,
  almost all of which are required by 1989 C standard.

.. _ISO 8601: https://www.iso.org/iso-8601-date-and-time-format.html
.. _format codes: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes