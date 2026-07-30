from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext


class CallApiContractError(RuntimeError):
    """API истории звонков вернул неожиданный контракт."""


def _require_json_object(
    status: int,
    text: str,
    body: Any,
    *,
    checkpoint: str,
) -> dict[str, Any]:
    if status != 200:
        raise CallApiContractError(
            f"{checkpoint} ожидали HTTP 200, получили {status}: {text}"
        )
    if not isinstance(body, dict):
        raise CallApiContractError(
            f"{checkpoint} ожидали JSON-объект, получили {body!r}"
        )
    return body


def list_operator_events(
    rop_request: APIRequestContext,
    operator_id: str,
    *,
    checkpoint: str,
    per_page: int = 6,
) -> list[dict[str, Any]]:
    body = get_operator_events_page(
        rop_request,
        operator_id,
        checkpoint=checkpoint,
        per_page=per_page,
    )
    items = body["items"]
    return items


def get_operator_events_page(
    rop_request: APIRequestContext,
    operator_id: str,
    *,
    checkpoint: str,
    page: int = 1,
    per_page: int = 30,
) -> dict[str, Any]:
    response = rop_request.get(
        "/v1/onlinepbx/events",
        params={
            "filter": f"operator_id='{operator_id}'",
            "page": page,
            "perPage": per_page,
        },
    )
    body = _require_json_object(
        response.status,
        response.text(),
        response.json(),
        checkpoint=checkpoint,
    )
    items = body.get("items")
    if not isinstance(items, list):
        raise CallApiContractError(
            f"{checkpoint} ожидали массив items, получили {body!r}"
        )
    if not all(isinstance(item, dict) for item in items):
        raise CallApiContractError(
            f"{checkpoint} список содержит не-объект: {items!r}"
        )
    return body


def get_event(
    rop_request: APIRequestContext,
    event_id: str,
    *,
    checkpoint: str,
) -> dict[str, Any]:
    response = rop_request.get(f"/v1/onlinepbx/events/{event_id}")
    return _require_json_object(
        response.status,
        response.text(),
        response.json(),
        checkpoint=checkpoint,
    )


def event_audio_url(event: dict[str, Any]) -> str:
    raw_payload = event.get("raw_payload")
    candidates: list[Any] = []
    if isinstance(raw_payload, dict):
        candidates.append(raw_payload.get("download_url"))
    candidates.append(event.get("download_url"))
    normalized = [
        candidate.strip()
        for candidate in candidates
        if isinstance(candidate, str) and candidate.strip()
    ]
    for candidate in normalized:
        if candidate.lower().startswith(("http://", "https://")):
            return candidate
    return normalized[0] if normalized else ""
