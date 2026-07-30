from __future__ import annotations

import time
from urllib.parse import urlsplit

from playwright.sync_api import ConsoleMessage, Page, Request, Response, expect


ESSENTIAL_RESOURCE_TYPES = frozenset(
    {"document", "script", "stylesheet", "font", "image"}
)


class DeploymentSmokePage:
    """Основные маршруты и диагностические события загрузки frontend."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.failed_resources: list[str] = []
        self.page_errors: list[str] = []
        self.console_errors: list[str] = []
        self._pending_resources: set[Request] = set()
        self._last_resource_activity = time.monotonic()

        page.on("request", self._record_started_request)
        page.on("requestfinished", self._record_finished_request)
        page.on("requestfailed", self._record_failed_request)
        page.on("response", self._record_failed_response)
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        page.on("console", self._record_console_error)

    def open_section(
        self,
        *,
        menu_name: str,
        expected_url: str,
        content_heading: str,
    ) -> None:
        self.page.get_by_role(
            "link",
            name=menu_name,
            exact=True,
        ).click()
        expect(
            self.page,
            f"[TC-375] после перехода «{menu_name}» ожидали {expected_url}",
        ).to_have_url(expected_url)
        expect(
            self.page.get_by_text(
                "Unexpected Application Error!",
                exact=True,
            ),
            f"[TC-375] раздел «{menu_name}» не должен падать в router error",
        ).to_have_count(0)
        expect(
            self.page.get_by_role(
                "heading",
                name=content_heading,
                exact=True,
            ),
            f"[TC-375] раздел «{menu_name}» должен отрисовать содержимое",
        ).to_be_visible()
        self.wait_for_resources()

    def reload(self, expected_url: str, *, content_heading: str) -> None:
        self.page.reload(wait_until="domcontentloaded")
        expect(
            self.page,
            "[TC-375] после обновления ожидали тот же адрес",
        ).to_have_url(expected_url)
        expect(
            self.page.get_by_text(
                "Unexpected Application Error!",
                exact=True,
            ),
            "[TC-375] обновление не должно приводить к router error",
        ).to_have_count(0)
        expect(
            self.page.get_by_role(
                "heading",
                name=content_heading,
                exact=True,
            ),
            "[TC-375] после reload должно появиться содержимое раздела",
        ).to_be_visible()
        self.wait_for_resources()

    def wait_for_resources(self, timeout_ms: int = 10_000) -> None:
        """Ждёт завершения chunks без ожидания долгоживущего SSE."""
        deadline = time.monotonic() + timeout_ms / 1000
        while time.monotonic() < deadline:
            quiet_for = time.monotonic() - self._last_resource_activity
            if not self._pending_resources and quiet_for >= 0.2:
                return
            self.page.wait_for_timeout(50)

        pending_paths = sorted(
            {
                self._safe_path(request.url)
                for request in self._pending_resources
            }
        )
        raise AssertionError(
            "[TC-375] frontend-ресурсы не завершили загрузку за "
            f"{timeout_ms} ms: {pending_paths!r}"
        )

    def assert_no_loading_errors(self) -> None:
        assert not self.failed_resources, (
            "[TC-375] обнаружены незагруженные frontend-ресурсы: "
            f"{sorted(set(self.failed_resources))!r}"
        )
        assert not self.page_errors, (
            "[TC-375] обнаружены необработанные JavaScript-ошибки; "
            f"количество={len(self.page_errors)}"
        )
        assert not self.console_errors, (
            "[TC-375] Console содержит JavaScript error; "
            f"количество={len(self.console_errors)}"
        )

    def _record_failed_request(self, request: Request) -> None:
        if not self._is_frontend_resource(request):
            return
        self._pending_resources.discard(request)
        self._last_resource_activity = time.monotonic()
        failure = request.failure or "network failure"
        # Chromium может отменить speculative preload и тут же повторно
        # запросить тот же module chunk обычным import. Это не ошибка загрузки:
        # недоступный chunk даёт ERR_FAILED/ERR_INTERNET_DISCONNECTED, Console
        # error и router error, которые проверяются отдельно.
        if failure == "net::ERR_ABORTED":
            return
        self.failed_resources.append(
            f"{request.resource_type} {self._safe_path(request.url)} "
            f"({failure})"
        )

    def _record_failed_response(self, response: Response) -> None:
        request = response.request
        if response.status < 400 or not self._is_frontend_resource(request):
            return
        self.failed_resources.append(
            f"{request.resource_type} {self._safe_path(response.url)} "
            f"(HTTP {response.status})"
        )

    def _record_started_request(self, request: Request) -> None:
        if not self._is_frontend_resource(request):
            return
        self._pending_resources.add(request)
        self._last_resource_activity = time.monotonic()

    def _record_finished_request(self, request: Request) -> None:
        if not self._is_frontend_resource(request):
            return
        self._pending_resources.discard(request)
        self._last_resource_activity = time.monotonic()

    def _record_console_error(self, message: ConsoleMessage) -> None:
        if message.type != "error":
            return
        self.console_errors.append(message.text)

    @staticmethod
    def _is_frontend_resource(request: Request) -> bool:
        path = urlsplit(request.url).path
        return (
            request.resource_type in ESSENTIAL_RESOURCE_TYPES
            or "/assets/" in path
        )

    @staticmethod
    def _safe_path(url: str) -> str:
        parsed = urlsplit(url)
        return parsed.path or "/"
