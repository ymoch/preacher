CLI Application
===============

Arguments
---------

Options
-------

.. list-table:: Preacher CLI Options
   :header-rows: 1
   :widths: 10, 20, 15, 40, 15

   * - Short
     - Long
     - Type
     - Description
     - Default
   * - ``-h``
     - ``--help``
     -
     - Show the help message and exit.
     -
   * - ``-v``
     - ``--version``
     -
     - Show program's version number and exit.
     -
   * - ``-u URL``
     - ``--url url``
     - string
     - Set the base URL.
     - http://localhost:5042
       (As the sample server)
   * - ``-l level``
     - ``--level level``
     - :ref:`level`
     - Show only above or equal to this level on the console
       (cannot affect other reports.)
     - success
   * - ``-r num``
     - ``--retry num``
     - int
     - Set the max retry count.
     - 0
   * - ``-d sec``
     - ``--delay sec``
     - float
     - Set the delay between attempts in seconds.
     - 0.1
   * - ``-t sec``
     - ``--timeout sec``
     - float
     - Set the request timeout in seconds.
     - no timeout
   * - ``-c num``
     - ``--concurrency num``
     - int
     - Set the request concurrency.
     - 1
   * - ``-R dir``
     - ``--report dir``
     - string
     - Set the report directory. (experimental)
     - no report


.. _level:

Level
^^^^^
Allowed values are:

- skipped
- success
- unstable
- failure
