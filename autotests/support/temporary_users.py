from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import APIRequestContext


@dataclass(frozen=True)
class OperatorDraft:
    username: str
    password: str
    first_name: str
    last_name: str
    phone: str
    pbx_extension: str
    salary: int
    salary_day: str

    def api_payload(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "pbx_extension": self.pbx_extension,
            "salary": self.salary,
            "salary_day": self.salary_day,
        }


@dataclass(frozen=True)
class TemporaryOperator:
    id: str
    username: str
    password: str
    first_name: str
    last_name: str
    phone: str
    pbx_extension: str
    salary: int
    salary_day: str
    rop_request: APIRequestContext
