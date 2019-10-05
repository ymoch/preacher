#######################################
Preacher: Flexible Web API Verification
#######################################

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
    :target: https://www.python.org/
.. image:: https://badge.fury.io/py/preacher.svg
    :target: https://badge.fury.io/py/preacher
.. image:: https://readthedocs.org/projects/preacher/badge/?version=latest
    :target: https://preacher.readthedocs.io/en/latest/?badge=latest
.. image:: https://circleci.com/gh/ymoch/preacher.svg?style=svg
    :target: https://circleci.com/gh/ymoch/preacher
.. image:: https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ymoch/preacher
.. image:: https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg
    :target: https://lgtm.com/projects/g/ymoch/preacher/context:python

Preacher verifies API servers,
which requests to API servers and verify the response along to given scenarios.

Scenarios are written in `YAML`_, bodies are analyzed `jq`_ or `XPath`_ queries
and validation rules are based on `Hamcrest`_ (`PyHamcrest`_)
so that any developers can write without learning toughly.

*******
Targets
*******
- Flexible validation to test with real backends: neither mocks nor sandboxes.
  - Matcher-based validation.
- CI Friendly to automate easily.
  - A CLI application and YAML-based scenarios.

*****
Usage
*****
Install from PyPI. Supports only Python 3.7+.

.. code-block:: sh

    pip install preacher

Write your own scenario.

.. code-block:: yaml

    # scenario.yml
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

Then, run ``preacher-cli`` command.

.. code-block:: sh

    pip install preacher
    preacher-cli -u http://your.domain.com/base scenario.yml

For more information, see the documentation: https://preacher.readthedocs.io/


*******
License
*******
.. image:: https://img.shields.io/badge/License-MIT-brightgreen.svg
    :target: https://opensource.org/licenses/MIT

Copyright (c) 2019 Yu MOCHIZUKI


.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _XPATH: https://www.w3.org/TR/xpath/all/
.. _Hamcrest: http://hamcrest.org/
.. _PyHamcrest: https://pyhamcrest.readthedocs.io/
