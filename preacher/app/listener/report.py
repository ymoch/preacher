from __future__ import annotations

import os
from typing import List

import jinja2

from preacher.core.request import Response
from preacher.core.scenario import ScenarioResult
from . import Listener


class ReportingListener(Listener):

    def __init__(self, path):
        self._path = path
        self._responses_path = os.path.join(self._path, 'responses')
        self._results: List[ScenarioResult] = []
        self._env = jinja2.Environment(
            loader=jinja2.PackageLoader('preacher', 'resources/html'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        self._initialize()

    def _initialize(self) -> None:
        os.makedirs(self._path, exist_ok=True)
        os.makedirs(self._responses_path, exist_ok=True)

    def on_response(self, response: Response) -> None:
        name = f'{response.id}.html'
        path = os.path.join(self._responses_path, name)
        with open(path, 'w') as f:
            self._env.get_template('view.html').stream(
                response=response,
            ).dump(f)

    def on_scenario(self, result: ScenarioResult) -> None:
        self._results.append(result)

    def on_end(self) -> None:
        html_path = os.path.join(self._path, 'index.html')
        with open(html_path, 'w') as f:
            self._env.get_template('index.html').stream(
               scenarios=self._results,
            ).dump(f)
