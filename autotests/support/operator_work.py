from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from typing import Any, Generator

from playwright.sync_api import (
    APIRequestContext,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from autotests.config import Settings
from autotests.support.auth_requests import login, require_access_token
from autotests.support.login_rate_guard import LoginRateGuard
from autotests.support.temporary_users import TemporaryOperator


SHIFT_PATH = "/v1/operator-work/shift"
BREAK_PATH = "/v1/operator-work/break"
WEEKLY_PATH = "/v1/operator-work/weekly"
WORK_PATH = "/dashboard/work"


@dataclass
class OperatorWorkHarness:
    operator: TemporaryOperator
    operator_request: APIRequestContext
    browser_context: BrowserContext
    page: Page
    access_token: str
    user: dict[str, Any]

    @property
    def today_key(self) -> str:
        return date.today().isoformat()

    def weekly_items(self, *, checkpoint: str) -> list[dict[str, Any]]:
        response = self.operator_request.get(WEEKLY_PATH)
        assert response.status == 200, (
            f"{checkpoint}: GET weekly ожидали 200, получили "
            f"{response.status}: {response.text()}"
        )
        body = response.json()
        assert isinstance(body, dict), (
            f"{checkpoint}: ожидали объект weekly, получили {body!r}"
        )
        raw_items = body.get("items")
        assert isinstance(raw_items, list), (
            f"{checkpoint}: ожидали список items, получили {body!r}"
        )
        return [item for item in raw_items if isinstance(item, dict)]

    def today_items(self, *, checkpoint: str) -> list[dict[str, Any]]:
        return [
            item
            for item in self.weekly_items(checkpoint=checkpoint)
            if item.get("work_date") == self.today_key
        ]

    def open_work_page(self, base_url: str) -> None:
        self.page.goto(
            f"{base_url}{WORK_PATH}",
            wait_until="commit",
        )

    def cleanup_today_shift(self) -> None:
        items = self.today_items(checkpoint="[operator-work cleanup]")
        if not items:
            return
        assert len(items) == 1, (
            "[operator-work cleanup] ожидали не более одной смены за сегодня, "
            f"получили {items!r}"
        )
        item = items[0]
        if item.get("active_break_started_at"):
            break_response = self.operator_request.post(BREAK_PATH)
            assert break_response.status == 200, (
                "[operator-work cleanup] завершение перерыва ожидало 200, "
                f"получили {break_response.status}: {break_response.text()}"
            )
            item = break_response.json().get("item", item)
        if not item.get("shift_closed_at"):
            shift_response = self.operator_request.post(SHIFT_PATH)
            assert shift_response.status == 200, (
                "[operator-work cleanup] завершение смены ожидало 200, "
                f"получили {shift_response.status}: {shift_response.text()}"
            )
        delete_response = self.operator_request.delete(
            SHIFT_PATH,
            params={"work_date": self.today_key},
        )
        assert delete_response.status == 204, (
            "[operator-work cleanup] удаление смены ожидало 204, получили "
            f"{delete_response.status}: {delete_response.text()}"
        )


def _authorize_page(
    page: Page,
    *,
    base_url: str,
    access_token: str,
    user: dict[str, Any],
) -> None:
    page.goto(base_url, wait_until="commit")
    page.evaluate(
        """([token, serializedUser]) => {
            window.localStorage.setItem('jwt_access_token', token);
            window.localStorage.setItem('jwt_user', serializedUser);
        }""",
        [access_token, json.dumps(user, ensure_ascii=False)],
    )


@contextmanager
def operator_work_harness(
    *,
    temporary_operator: TemporaryOperator,
    browser: Browser,
    browser_context_args: dict[str, object],
    playwright: Playwright,
    test_settings: Settings,
    login_rate_guard: LoginRateGuard,
) -> Generator[OperatorWorkHarness, None, None]:
    anonymous_request = playwright.request.new_context(
        base_url=test_settings.require_api_base_url(),
        extra_http_headers={"Content-Type": "application/json"},
    )
    operator_request: APIRequestContext | None = None
    browser_context: BrowserContext | None = None
    harness: OperatorWorkHarness | None = None

    try:
        login_response = login(
            anonymous_request,
            login_rate_guard,
            username=temporary_operator.username,
            password=temporary_operator.password,
        )
        access_token, user = require_access_token(
            login_response,
            checkpoint="[operator-work setup] вход временного оператора",
        )
        assert user.get("id") == temporary_operator.id, (
            "[operator-work setup] после входа получен другой оператор"
        )
        operator_request = playwright.request.new_context(
            base_url=test_settings.require_api_base_url(),
            extra_http_headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        browser_context = browser.new_context(**browser_context_args)
        page = browser_context.new_page()
        _authorize_page(
            page,
            base_url=test_settings.web_base_url,
            access_token=access_token,
            user=user,
        )
        harness = OperatorWorkHarness(
            operator=temporary_operator,
            operator_request=operator_request,
            browser_context=browser_context,
            page=page,
            access_token=access_token,
            user=user,
        )
        yield harness
    finally:
        if harness is not None:
            harness.cleanup_today_shift()
        if browser_context is not None:
            browser_context.close()
        if operator_request is not None:
            operator_request.dispose()
        anonymous_request.dispose()
