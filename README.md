# Preacher: Flexible Web API Verification

[![PyPI version](https://badge.fury.io/py/preacher.svg)](https://badge.fury.io/py/preacher)
[![Documentation Status](https://readthedocs.org/projects/preacher/badge/?version=latest)](https://preacher.readthedocs.io/en/latest/?badge=latest)
[![CircleCI](https://circleci.com/gh/ymoch/preacher.svg?style=svg)](https://circleci.com/gh/ymoch/preacher)
[![codecov](https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg)](https://codecov.io/gh/ymoch/preacher)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/ymoch/preacher/context:python)

which requests to API servers and verify the response along to given scenarios.

Scenarios are written in [YAML][], bodies are analyzed [jq][] or [XPath][] queries
and validation rules are based on [Hamcrest][] ([PyHamcrest][])
so that any developers can write without learning toughly.

Full documentation is available: [https://preacher.readthedocs.io/]

[YAML]: https://yaml.org/
[jq]: https://stedolan.github.io/jq/
[XPath]: https://www.w3.org/TR/xpath/all/
[Hamcrest]: http://hamcrest.org/
[PyHamcrest]: https://pyhamcrest.readthedocs.io/
