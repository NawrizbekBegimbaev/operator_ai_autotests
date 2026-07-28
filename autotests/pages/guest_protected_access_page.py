from __future__ import annotations

import re
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page


class GuestProtectedAccessPage:
    """Защищённые маршруты, открываемые без авторизации."""

    _DOM_OBSERVER_SCRIPT = """
        const protectedMarkers = [
          "Название сделки",
          "Компании РОП",
          "Временные параметры очереди звонков"
        ];
        const recordProtectedMarkers = () => {
          const pageText = document.body?.innerText ?? "";
          for (const marker of protectedMarkers) {
            if (pageText.includes(marker)) {
              window.__qaRecordGuestProtectedMarker(marker);
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
        self.protected_content: dict[str, dict[str, Locator]] = {
            "/dashboard/calls": {
                "таблица звонков": page.get_by_role("table"),
            },
            "/dashboard/rop": {
                "заголовок компаний РОП": page.get_by_role(
                    "heading",
                    name=re.compile(r"^Компании РОП · \d+$"),
                ),
            },
            "/dashboard/mezonlar": {
                "заголовок «Критерии»": page.get_by_role(
                    "heading",
                    name="Критерии",
                    exact=True,
                ),
            },
        }
        self._observed_dom_markers: list[str] = []
        self.page.expose_binding(
            "__qaRecordGuestProtectedMarker",
            self._record_protected_marker,
        )
        self.page.add_init_script(script=self._DOM_OBSERVER_SCRIPT)

    def open_protected_route(self, base_url: str, route_path: str) -> None:
        self._observed_dom_markers.clear()
        self.page.goto(urljoin(f"{base_url}/", route_path.lstrip("/")))

    def observed_dom_markers(self) -> list[str]:
        return list(self._observed_dom_markers)

    def _record_protected_marker(self, _source: object, marker: str) -> None:
        if marker not in self._observed_dom_markers:
            self._observed_dom_markers.append(marker)
