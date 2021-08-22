YAML Tag
========

``!argument``: Define an argument
---------------------------------
Using ``!argument`` tag, you can define an argument placeholder,
which is filled with argument options given on run time or :ref:`parameterized-test`.

A not filled argument is regarded as ``null`` value.

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
A ``Duration`` is given as a combination of one or more string values in particular formats.

- When given time such like ``12:34+01:00``, then uses the combination of the relative date and the given time.
    - When given plural time like ``12:34+01:00 23:45+02:00``,
      even though it has no reasonable meaning,
      then uses the last part (``23:45+02:00``).
- When given an offset, then uses the datetime that the request starts.
    - Days, hours, minutes and seconds offsets are available.
    - When given a positive offset like ``1 day`` or ``+2 hours``, then uses the future datetime.
    - When given a negative offset like ``-1 minute`` or ``-2 seconds``, then uses the past datetime.
    - When given plural offsets like, then uses the total offset.
        - ``1 hour 2 minutes`` means "62 minutes later".
        - Note that ``-1 hour 2 minutes`` means "58 minutes ago".
          It is interpreted as ``-1 hour`` *plus* ``+2 minutes``.
- ``now`` means zero offset, the same as ``0 second``.

Here are some examples:

- ``now``: just the evaluation starts.
- ``1 day``: after a day later.
- ``+1 hour +1 minute``: an hour and a minute later.
- ``-1 hour -2 minutes``: an hour and two minutes ago.
- ``12:34+01:00``: the combination of the date that the evaluation starts
  and time 12:34 with an hour time difference between London.
- ``+1 day +2 hour 12:34+01:00``:
  the combination of the date that is an hour and two minute later
  and time 12:34 with an hour time difference between London.

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