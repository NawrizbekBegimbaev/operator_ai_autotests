from __future__ import annotations

import pytest
from playwright.sync_api import APIRequestContext


@pytest.mark.api
@pytest.mark.high
@pytest.mark.positive
@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG-046: действующее подключение AmoCRM возвращает 409 при "
        "повторной синхронизации структуры"
    ),
)
def test_bug_046_connected_amocrm_repeated_structure_sync_succeeds(
    rop_api_request: APIRequestContext,
) -> None:
    """Повторная синхронизация подключённой AmoCRM остаётся рабочим happy-path."""
    response = rop_api_request.post("/v1/amocrm/pipelines/sync")
    assert response.status == 200, (
        "[BUG-046] повторная синхронизация подключённой AmoCRM должна "
        f"вернуть 200, получено {response.status}."
    )
    body = response.json()
    assert isinstance(body, dict)
    items = body.get("items")
    assert isinstance(items, list) and items, (
        "[BUG-046] после синхронизации должен вернуться непустой список "
        "воронок."
    )
