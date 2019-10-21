Quickstart
==========

Install
-------
Preacher is available on `PyPI`_ and can be installed by `pip`_.

.. code-block:: sh

    $ pip install preacher

.. note:: Preacher supports only Python 3.7+.


Writing Your Own Scenarios
--------------------------
Here is a very simple example.

.. code-block:: yaml

    label: An example of a scenario
    cases:
      - label: An example of a case
        request: /path/to/foo
        response:
          status_code: 200
          body:
            - describe: .foo
              should:
                equal: bar

Verify the Servers
------------------

.. code-block:: sh

    $ preacher-cli -u https://your-server.com/base scenario.yml


.. _PyPI: https://pypi.org/project/preacher/
.. _pip: https://pip.pypa.io/en/stable/
