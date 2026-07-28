from __future__ import annotations

from playwright.sync_api import Page, Request


def track_requests(
    page: Page,
    *,
    method: str,
    url_suffix: str,
) -> list[Request]:
    matched_requests: list[Request] = []

    def record_request(request: Request) -> None:
        if request.method == method and request.url.endswith(url_suffix):
            matched_requests.append(request)

    page.on("request", record_request)
    return matched_requests
