from __future__ import annotations

import re
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import Locator, Page, Response


class DirectUrlAccessPage:
    """Проверка защищённых разделов, открытых по прямому URL."""

    PROTECTED_ENDPOINTS = {
        "/dashboard/rop": "/v1/users",
        "/dashboard/leads": "/v1/leads",
        "/dashboard/plans": "/v1/plans",
    }

    _DOM_OBSERVER_SCRIPT = """
        const seenProtectedMarkers = [];
        const protectedMarkers = [
          "Компании РОП",
          "Лиды · ",
          "Управляйте ценой, названием и возможностями здесь"
        ];
        const recordProtectedMarkers = () => {
          const pageText = document.body?.innerText ?? "";
          for (const marker of protectedMarkers) {
            if (
              pageText.includes(marker) &&
              !seenProtectedMarkers.includes(marker)
            ) {
              seenProtectedMarkers.push(marker);
              window.__qaRecordProtectedMarker(marker);
            }
          }
        };
        new MutationObserver(recordProtectedMarkers).observe(document, {
          childList: true,
          subtree: true,
          characterData: true
        });
        document.addEventListener("DOMContentLoaded", recordProtectedMarkers);
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.forbidden_heading = page.get_by_role(
            "heading",
            name="Permission denied",
            exact=True,
        )
        self.protected_content: dict[str, dict[str, Locator]] = {
            "/dashboard/rop": {
                "заголовок списка компаний РОП": page.get_by_role(
                    "heading",
                    name=re.compile(r"^Компании РОП · \d+$"),
                ),
            },
            "/dashboard/leads": {
                "заголовок списка лидов": page.get_by_role(
                    "heading",
                    name=re.compile(r"^Лиды · \d+$"),
                ),
            },
            "/dashboard/plans": {
                "заголовок управления тарифами": page.get_by_role(
                    "heading",
                    name="Тарифы",
                    exact=True,
                ),
            },
        }
        self.protected_responses: list[tuple[int, str]] = []
        self._observed_dom_markers: list[str] = []
        self._observed_endpoint = ""
        self.page.expose_binding(
            "__qaRecordProtectedMarker",
            self._record_protected_marker,
        )
        self.page.add_init_script(script=self._DOM_OBSERVER_SCRIPT)
        self.page.on("response", self._record_protected_response)

    def open_protected_route(self, base_url: str, route_path: str) -> None:
        self.protected_responses.clear()
        self._observed_dom_markers.clear()
        self._observed_endpoint = self.PROTECTED_ENDPOINTS[route_path]
        self.page.goto(urljoin(f"{base_url}/", route_path.lstrip("/")))

    def observed_dom_markers(self) -> list[str]:
        return list(self._observed_dom_markers)

    def _record_protected_response(self, response: Response) -> None:
        if urlsplit(response.url).path == self._observed_endpoint:
            self.protected_responses.append((response.status, response.url))

    def _record_protected_marker(self, _source: object, marker: str) -> None:
        if marker not in self._observed_dom_markers:
            self._observed_dom_markers.append(marker)
