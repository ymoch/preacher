Quickstart
==========

Install
-------

``pip install preacher``
^^^^^^^^^^^^^^^^^^^^^^^^
Preacher is published to `PyPI`_ and can be installed by `pip`_.
This is the most basic way to install Preacher.

If you have Python runtime environment,
let's install Preacher and see its version.

.. code-block:: sh

    $ pip install preacher
    $ preacher-cli --version

.. note:: Preacher supports only Python 3.7+.

Running on `Docker`_
^^^^^^^^^^^^^^^^^^^^
We provide `Docker`_ images on `Docker Hub`_
to avoid problems caused by environments.
By default, the container working directory is ``/work``,
and the host directory may be mounted here as below.

.. code-block:: sh

    $ docker pull ymoch/preacher
    $ docker run -v $PWD:/work -t ymoch/preacher preacher-cli --version

In several cases (such as below), Preacher will not work on your environment.
Running on Docker will solve these problems.

- You don't want to install Python.
- Your Python is too older to run Preacher.
- Your Python environment cannot accept `C extensions`_.
  Preacher depends on `lxml`_ and `pyjq`_, which contain C extensions.

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

Test Report
-----------
Preacher can export a rich test report in HTML format,
which visualize test results and provide actual responses.

When given a directory path in ``-R`` or ``--report`` option,
Preacher exports the test report to that directory.
The directory is automatically created.
When given ``path/to/report`` as a report directory path,
``path/to/report/index.html`` should be the entry point.
When running Preacher on CI, you may save the report as a build artifact.


.. _PyPI: https://pypi.org/project/preacher/
.. _Docker: https://www.docker.com/
.. _Docker Hub: https://hub.docker.com/r/ymoch/preacher
.. _pip: https://pip.pypa.io/en/stable/
.. _lxml: https://lxml.de/
.. _pyjq: https://github.com/doloopwhile/pyjq
.. _C extensions: https://docs.python.org/ja/3/extending/extending.html
