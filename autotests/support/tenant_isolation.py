from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from playwright.sync_api import APIRequestContext


@dataclass(frozen=True)
class TenantActor:
    """Одна сторона межклиентской проверки."""

    rop: dict[str, Any]
    operator: dict[str, Any]
    rop_token: str
    operator_token: str = ""


@dataclass(frozen=True)
class CrossTenantContext:
    """
    Реальная компания-источник и временная компания-проверяющий.

    Временные РОП и оператор существуют только во время pytest-сессии
    и удаляются фикстурой независимо от результата тестов.
    """

    source: TenantActor
    outsider: TenantActor
    source_rop_request: APIRequestContext
    outsider_rop_request: APIRequestContext
    outsider_operator_request: APIRequestContext
