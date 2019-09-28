from __future__ import annotations

import os
from typing import List

import jinja2

from preacher.core.scenario import ScenarioResult
from . import Listener


class ReportingListener(Listener):

    def __init__(self, path):
        self._path = path

    def __enter__(self) -> ReportingListener:
        self._results: List[ScenarioResult] = []
        os.makedirs(self._path, exist_ok=True)
        return self

    def __exit__(self, ex_type, ex_value, trace) -> None:
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('preacher', 'resources/html'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        html_path = os.path.join(self._path, 'index.html')
        with open(html_path, 'w') as f:
            env.get_template('index.html').stream(
                scenarios=self._results,
            ).dump(f)

    def accept(self, result: ScenarioResult) -> None:
        self._results.append(result)
