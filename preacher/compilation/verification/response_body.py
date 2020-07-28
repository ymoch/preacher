from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from preacher.compilation.util.type import or_else
from preacher.core.verification import ResponseBodyDescription, Description

_KEY_DESCRIPTIONS = 'descriptions'


@dataclass(frozen=True)
class ResponseBodyDescriptionCompiled:
    descriptions: Optional[List[Description]] = None

    def replace(self, other: ResponseBodyDescriptionCompiled) -> ResponseBodyDescriptionCompiled:
        return ResponseBodyDescriptionCompiled(or_else(other.descriptions, self.descriptions))

    def fix(self) -> ResponseBodyDescription:
        return ResponseBodyDescription(self.descriptions)
