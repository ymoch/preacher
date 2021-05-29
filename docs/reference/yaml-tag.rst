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
