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

Running on Docker
^^^^^^^^^^^^^^^^^
If you don't have Python or have minimal Python environment,
Preacher possibly does not work.
We have Docker images on `Docker Hub`_
to avoid problems caused by environments.

.. code-block:: sh

    $ docker pull ymoch/preacher
    $ docker run -t ymoch/preacher preacher-cli --version

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


.. _pip: https://pip.pypa.io/en/stable/
.. _PyPI: https://pypi.org/project/preacher/
.. _Docker Hub: https://cloud.docker.com/u/ymoch/repository/docker/ymoch/preacher
