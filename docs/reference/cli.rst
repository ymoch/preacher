CLI Application
===============

Arguments
---------
Scenario YAML file paths.

When given none, the standard input is used instead
and the current directory is regarded as the base directory.

Options
-------

.. list-table:: Preacher CLI Options
   :header-rows: 1

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
   * -
     - ``--version``
     -
     - Show program's version number and exit.
     -
   * - ``-u URL``
     - ``--base-url url``
     - string
     - Set the base URL.
     - ``''``
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

Environment Variables Interface
-------------------------------
Using commandline options bother us in some situation like:

- Giving CI build parameters to Preacher.
- Wrapping Preacher execution with shell scripts.

Alternatively, Preacher supports environment variables
that are equivalent to commandline options.

.. list-table:: Environment variables instead of commandline options
   :header-rows: 1

   * - Name
     - Equivalent to
   * - ``PREACHER_CLI_BASE_URL``
     - ``-u``, ``--base-url``
   * - ``PREACHER_CLI_LEVEL``
     - ``-l``, ``--level``
   * - ``PREACHER_CLI_RETRY``
     - ``-r``, ``--retry``
   * - ``PREACHER_CLI_DELAY``
     - ``-d``, ``--delay``
   * - ``PREACHER_CLI_TIMEOUT``
     - ``-t``, ``--timeout``
   * - ``PREACHER_CLI_CONCURRENCY``
     - ``-c``, ``--concurrency``
   * - ``PREACHER_CLI_REPORT``
     - ``-r``, ``--report``

Environment variables that have empty strings are ignored.
This behavior is useful to handle optional settings.

Preacher requests your server using `requests`_,
which allows you to pass environment variables that `requests`_ supports.
For example, when you want to proxy requests,
you can achieve it by ``HTTP_PROXY`` or ``HTTPS_PROXY`` variable.

.. code-block:: sh

    $ HTTP_PROXY=http://proxy.com:3128 preacher-cli scenario.yml


.. _requests: https://requests.kennethreitz.org/
