from __future__ import annotations

import re
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import Locator, Page, Request, Response


class DirectUrlAccessPage:
    """Проверка защищённых разделов, открытых по прямому URL."""

    CALLING_CAPTURE_ENDPOINTS = frozenset(
        {
            "/v1/calling/queue",
            "/v1/calling/next",
        }
    )

    PROTECTED_ENDPOINT_PATTERNS = {
        "/dashboard/rop": (re.compile(r"^/v1/users$"),),
        "/dashboard/leads": (re.compile(r"^/v1/leads$"),),
        "/dashboard/plans": (re.compile(r"^/v1/plans$"),),
        "/dashboard/calling": (
            re.compile(r"^/v1/calling/(?:queue|next)$"),
        ),
        "/dashboard/work": (
            re.compile(r"^/v1/operator-work/weekly$"),
        ),
        "/dashboard/home": (
            re.compile(
                r"^/v1/(?:calling/queue|operator-work/weekly|amocrm/deals)$"
            ),
        ),
        "/dashboard/calls": (
            re.compile(r"^/v1/amocrm/deals(?:/stream)?$"),
        ),
        "/dashboard/dynamic-form": (
            re.compile(
                r"^/v1/amocrm/(?:statuses|pipelines(?:/selected)?|"
                r"forms(?:/[^/]+/fields)?)$"
            ),
            re.compile(r"^/v1/dynamic-form/forms$"),
        ),
        "/dashboard/mezonlar": (
            re.compile(r"^/v1/calling/settings$"),
            re.compile(r"^/v1/users/[^/]+/company-description$"),
        ),
        "/dashboard/operator-pipelines": (
            re.compile(r"^/v1/users$"),
            re.compile(r"^/v1/calling/assignable-pipelines$"),
            re.compile(r"^/v1/operator-pipelines(?:/.*)?$"),
        ),
        "/dashboard/attendance": (
            re.compile(r"^/v1/operator-work/weekly$"),
        ),
    }

    _DOM_OBSERVER_SCRIPT = """
        const seenProtectedMarkers = [];
        const protectedMarkersByPath = {
          "/dashboard/rop": ["Компании РОП"],
          "/dashboard/leads": ["Лиды · "],
          "/dashboard/plans": [
            "Управляйте ценой, названием и возможностями здесь"
          ],
          "/dashboard/calling": ["Обзвон", "лидов в очереди"],
          "/dashboard/work": ["Рабочее время"],
          "/dashboard/home": ["Последние звонки"],
          "/dashboard/calls": ["Звонки"],
          "/dashboard/dynamic-form": ["Статусы лида"],
          "/dashboard/mezonlar": ["Критерии"],
          "/dashboard/operator-pipelines": ["Настройка очереди"],
          "/dashboard/attendance": ["Посещаемость"]
        };
        const protectedMarkers =
          protectedMarkersByPath[window.location.pathname] ?? [];
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
        self.protected_content.update(
            {
                "/dashboard/calling": {
                    "заголовок режима обзвона": page.get_by_role(
                        "heading",
                        name="Обзвон",
                        exact=True,
                    ),
                },
                "/dashboard/work": {
                    "заголовок рабочего времени": page.get_by_role(
                        "heading",
                        name="Рабочее время",
                        exact=True,
                    ),
                },
                "/dashboard/home": {
                    "заголовок последних звонков": page.get_by_role(
                        "heading",
                        name="Последние звонки",
                        exact=True,
                    ),
                },
                "/dashboard/calls": {
                    "заголовок таблицы лидов оператора": page.get_by_role(
                        "heading",
                        name="Звонки",
                        exact=True,
                    ),
                },
                "/dashboard/dynamic-form": {
                    "заголовок правил по статусам лида": page.get_by_role(
                        "heading",
                        name="Статусы лида",
                        exact=True,
                    ),
                },
                "/dashboard/mezonlar": {
                    "заголовок критериев": page.get_by_role(
                        "heading",
                        name="Критерии",
                        exact=True,
                    ),
                },
                "/dashboard/operator-pipelines": {
                    "заголовок настройки очереди": page.get_by_role(
                        "heading",
                        name="Настройка очереди",
                        exact=True,
                    ),
                },
                "/dashboard/attendance": {
                    "заголовок посещаемости": page.get_by_role(
                        "heading",
                        name="Посещаемость",
                        exact=True,
                    ),
                },
            }
        )
        self.protected_responses: list[tuple[int, str]] = []
        self.protected_requests: list[str] = []
        self._observed_dom_markers: list[str] = []
        self._observed_endpoint_patterns: tuple[re.Pattern[str], ...] = ()
        self.page.expose_binding(
            "__qaRecordProtectedMarker",
            self._record_protected_marker,
        )
        self.page.add_init_script(script=self._DOM_OBSERVER_SCRIPT)
        self.page.on("request", self._record_protected_request)
        self.page.on("response", self._record_protected_response)

    def open_protected_route(self, base_url: str, route_path: str) -> None:
        self.protected_responses.clear()
        self.protected_requests.clear()
        self._observed_dom_markers.clear()
        self._observed_endpoint_patterns = self.PROTECTED_ENDPOINT_PATTERNS[
            route_path
        ]
        self.page.goto(urljoin(f"{base_url}/", route_path.lstrip("/")))

    def observed_dom_markers(self) -> list[str]:
        return list(self._observed_dom_markers)

    def _record_protected_request(self, request: Request) -> None:
        request_path = urlsplit(request.url).path
        if self._matches_observed_endpoint(request_path):
            self.protected_requests.append(request_path)

    def _record_protected_response(self, response: Response) -> None:
        response_path = urlsplit(response.url).path
        if self._matches_observed_endpoint(response_path):
            self.protected_responses.append((response.status, response_path))

    def _record_protected_marker(self, _source: object, marker: str) -> None:
        if marker not in self._observed_dom_markers:
            self._observed_dom_markers.append(marker)

    def _matches_observed_endpoint(self, path: str) -> bool:
        return any(
            pattern.fullmatch(path)
            for pattern in self._observed_endpoint_patterns
        )
