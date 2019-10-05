Preacher: Flexible Web API Verification
=======================================

.. image:: https://img.shields.io/badge/python-3.7+-blue.svg
    :target: https://www.python.org/
.. image:: https://badge.fury.io/py/preacher.svg
    :target: https://badge.fury.io/py/preacher
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

The User Guide
--------------

.. toctree::
   :maxdepth: 3

   user/intro
   user/install
   user/quickstart
   user/scenario-structure
   user/matcher


.. _YAML: https://yaml.org/
.. _jq: https://stedolan.github.io/jq/
.. _XPATH: https://www.w3.org/TR/xpath/all/
.. _Hamcrest: http://hamcrest.org/
.. _PyHamcrest: https://pyhamcrest.readthedocs.io/
