Quickstart
==========

Install
-------

``pip install preacher``
^^^^^^^^^^^^^^^^^^^^^^^^
Preacher is written in Python, published to `PyPI`_
and can be installed by `pip`_.
This is the most basic way to install Preacher.

There are some requirements to install Preacher by `pip`_
due to the dependent packages.
If you feel annoyed, see :ref:`docker-run`.

- Preacher supports only Python 3.7+.
- Python C headers are required to build C extensions,
  which are available by installing Python develop packages
  or installing Python by source code build.
- On Linux, ``libxml2`` and ``libxslt`` are required by `lxml`_,
  as `official documentation <https://lxml.de/installation.html#requirements>`_ says.
- `jq.py`_ requires ``autoconf``, ``automake``, ``libtool``, ``make``
  and a C compiler such as ``gcc``.

Unfortunately, **Preacher doesn't support Windows now**
due to the dependent package `jq.py`_,
which `cannot be built on Windows <https://github.com/mwilliamson/jq.py/issues/20>`_.

If you have satisfied environment,
let's install Preacher and see its version.
If not, see :ref:`docker-run`.

.. code-block:: sh

    $ pip install preacher
    $ preacher-cli --version

.. _docker-run:

Running on `Docker`_
^^^^^^^^^^^^^^^^^^^^
We provide `Docker`_ images on `Docker Hub`_
to avoid problems caused by environments and dependencies.
By default, the container working directory is ``/work``,
and the host directory may be mounted here as below.

.. code-block:: sh

    $ docker pull ymoch/preacher
    $ docker run -v $PWD:/work:rw -t ymoch/preacher preacher-cli --version

Verify Your API
---------------
First, write your own test scenario.
Here is a very simple example of test scenarios.

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

Then, let's run Preacher to verify your API.

.. code-block:: sh

    $ preacher-cli -u https://your-server.com/base scenario.yml

Now, you have Preacher test results shown on your console.

Interpret Results
-----------------

Exit Statuses
^^^^^^^^^^^^^
When all tests succeeds,
``preacher-cli`` command returns ``0`` as a exit status.
When any of tests fails or command fails, it returns not ``0``.
Exit statuses are important for CI automation.

.. code-block:: sh

    $ echo $?

Verification Statuses
^^^^^^^^^^^^^^^^^^^^^
Each verification result has a "Verification Status."

.. list-table:: The List of Verification Statuses
   :header-rows: 1
   :widths: 10 20 50

   * - Value
     - Will Succeed?
     - Description
   * - ``SKIPPED``
     - yes
     - It wasn't needed to run.
   * - ``SUCCESS``
     - yes
     - It was satisfied.
   * - ``UNSTABLE``
     - no
     - It wasn't satisfied.
   * - ``FAILURE``
     - no
     - It encountered an unexpected situation and failed.


.. _PyPI: https://pypi.org/project/preacher/
.. _Docker: https://www.docker.com/
.. _Docker Hub: https://hub.docker.com/r/ymoch/preacher
.. _pip: https://pip.pypa.io/en/stable/
.. _lxml: https://lxml.de/
.. _jq.py: https://github.com/mwilliamson/jq.py
.. _C extensions: https://docs.python.org/ja/3/extending/extending.html
