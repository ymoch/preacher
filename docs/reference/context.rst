Context
=======
``Context`` is mutable meta information on execution.

Contextual Value Usage
----------------------
Contextual values are available in :ref:`Contextual Scenario<contextual-scenario>`.

.. code-block:: yaml

    when:
      describe:
        key: starts
      should:
        be_after: 2021-12-31T12:34:56Z

Contextual values are also available in request parameters via ``!context`` tag.

.. code-block:: yaml

    request:
      params:
        redirect-url: !context base_url

Define a contextual value
-------------------------

On :ref:`descriptions<description>`,
you can name the described value the given name as a contextual value.

.. code-block:: yaml

    describe: .foo.bar
    as: foo-bar

A contextual value live until the scenario ends, which doesn't contain subscenarios.

.. note::

    Contextual values are available in only ordered scenarios.

Predefined context
------------------
.. list-table:: The Definition of Predefined Context
   :header-rows: 1
   :widths: 15 15 40 30

   * - Key
     - Type
     - Description
     - Example
   * - starts
     - DateTime
     - When the execution starts.
     - ``2019-01-23T12:34:56.123456+00:00``
   * - base_url
     - String
     - The base URL
     - ``http://localhost:5042/base``
