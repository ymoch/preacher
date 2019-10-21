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

.. code-block:: sh

    $ docker pull ymoch/preacher
    $ docker run -t ymoch/preacher preacher-cli --version

In several cases (such as below), Preacher will not work on your environment.
Running on Docker will solve these problems.

- You don't want to install Python.
- Your Python is too older to run Preacher.
- Your Python environment cannot accept `C extensions`_.
  Preacher depends on `lxml`_ and `pyjq`_, which contain C extensions.

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
.. _Docker: https://www.docker.com/
.. _Docker Hub: https://cloud.docker.com/u/ymoch/repository/docker/ymoch/preacher
.. _pip: https://pip.pypa.io/en/stable/
.. _lxml: https://lxml.de/
.. _pyjq: https://github.com/doloopwhile/pyjq
.. _C extensions: https://docs.python.org/ja/3/extending/extending.html
