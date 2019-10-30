from __future__ import annotations

import dataclasses
import datetime
import json
import os
from typing import List, Any

import jinja2

from preacher.core.request import Response
from preacher.core.scenario import ScenarioResult
from . import Listener


def _json_serial(obj: Any) -> Any:
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(
        f'Object of type {obj.__class__.__name__} is not JSON serializable'
    )


class ReportingListener(Listener):

    def __init__(self, path):
        self._path = path
        self._responses_path = os.path.join(self._path, 'responses')
        self._results: List[ScenarioResult] = []

        self._initialize()

    def _initialize(self) -> None:
        os.makedirs(self._path, exist_ok=True)
        os.makedirs(self._responses_path, exist_ok=True)

    def on_response(self, response: Response) -> None:
        record = dataclasses.asdict(response)

        name = f'{response.id}.json'
        path = os.path.join(self._responses_path, name)
        with open(path, 'w') as f:
            json.dump(record, f, default=_json_serial)

    def on_scenario(self, result: ScenarioResult) -> None:
        self._results.append(result)

    def on_end(self) -> None:
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('preacher', 'resources/html'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        html_path = os.path.join(self._path, 'index.html')
        with open(html_path, 'w') as f:
            env.get_template('index.html').stream(
               scenarios=self._results,
            ).dump(f)

        view_path = os.path.join(self._path, 'view.html')
        with open(view_path, 'w') as f:
            env.get_template('view.html').stream().dump(f)
