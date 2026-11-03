from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass
class APIDataClass:
    name: str
    payload: dict[str, Any]
    expected_status: int
    expected_schema: type[BaseModel]
    expected_headers: dict[str, str]
    expected_body_values: dict[str, Any]
