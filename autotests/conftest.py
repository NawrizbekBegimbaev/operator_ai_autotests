from __future__ import annotations

import re
from collections.abc import Callable, Generator
from pathlib import Path
from threading import Lock
from typing import Any

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, expect
from playwright.sync_api import Playwright

from autotests.config import ConfigurationError, Settings
from autotests.pages.login_page import LoginPage


StorageState = dict[str, Any]
RoleStorageStateProvider = Callable[[str], StorageState]
AuthorizedPageFactory = Callable[[str], Page]
RoleApiTokenProvider = Callable[[str], str]

ROLE_START_PATHS = {
    "superadmin": "/dashboard/rop",
    "rop": "/dashboard/dynamic-form",
    "operator": "/dashboard/home",
}


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    try:
        return Settings.from_env()
    except ConfigurationError as error:
        raise pytest.UsageError(str(error)) from error


@pytest.fixture(scope="session")
def api_base_url(test_settings: Settings) -> str:
    try:
        return test_settings.require_api_base_url()
    except ConfigurationError as error:
        raise pytest.UsageError(str(error)) from error


@pytest.fixture(scope="session")
def role_api_token(
    playwright: Playwright,
    api_base_url: str,
    test_settings: Settings,
) -> RoleApiTokenProvider:
    """Ленивый session-кэш API-токена для каждой роли под lock."""
    cached_tokens: dict[str, str] = {}
    cache_lock = Lock()

    def get_api_token(role: str) -> str:
        with cache_lock:
            if role in cached_tokens:
                return cached_tokens[role]

            username, password = _credentials_for_role(
                test_settings,
                role,
            )
            request_context = playwright.request.new_context(
                base_url=api_base_url,
            )
            try:
                response = request_context.post(
                    "/v1/auth/login",
                    data={
                        "username": username,
                        "password": password,
                    },
                )
                actual_status = response.status
                response_text = response.text()
                body = response.json()
            finally:
                request_context.dispose()

            assert actual_status == 200, (
                f"[api_token:{role}] ожидали 200 при служебном входе, "
                f"получили {actual_status}: {response_text}"
            )
            assert isinstance(body, dict), (
                f"[api_token:{role}] ожидали JSON-объект входа, "
                f"получили {body!r}"
            )
            user = body.get("user")
            assert isinstance(user, dict), (
                f"[api_token:{role}] ожидали объект user, "
                f"получили {user!r}: {body!r}"
            )
            expected_api_role = {
                "superadmin": "super_admin",
                "rop": "rop",
                "operator": "operator",
            }[role]
            assert user.get("role") == expected_api_role, (
                f"[api_token:{role}] ожидали role={expected_api_role!r}, "
                f"получили {user.get('role')!r}: {user!r}"
            )
            access_token = body.get("access_token")
            assert isinstance(access_token, str) and access_token, (
                f"[api_token:{role}] ожидали непустой access_token: "
                f"{body!r}"
            )
            cached_tokens[role] = access_token
            return cached_tokens[role]

    return get_api_token


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, object],
) -> dict[str, object]:
    return {
        **browser_context_args,
        "locale": "ru-RU",
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture
def clean_login_page(page: Page) -> Generator[Page, None, None]:
    """Новая неавторизованная страница для тестов самого входа."""
    page.context.clear_cookies()
    yield page


def _credentials_for_role(settings: Settings, role: str) -> tuple[str, str]:
    if role == "superadmin":
        return settings.superadmin_username, settings.superadmin_password

    credentials = settings.credentials_for(role)
    return credentials.username, credentials.password


@pytest.fixture(scope="session")
def role_storage_state(
    browser: Browser,
    browser_context_args: dict[str, object],
    test_settings: Settings,
) -> RoleStorageStateProvider:
    """Ленивый session-кэш авторизованного состояния для каждой роли."""
    cached_states: dict[str, StorageState] = {}
    cache_lock = Lock()

    def get_storage_state(role: str) -> StorageState:
        if role not in ROLE_START_PATHS:
            raise pytest.UsageError(f"Неизвестная роль для UI-сессии: {role!r}.")

        with cache_lock:
            if role in cached_states:
                return cached_states[role]

            username, password = _credentials_for_role(test_settings, role)
            context = browser.new_context(**browser_context_args)
            try:
                page = context.new_page()
                login_page = LoginPage(page)

                login_page.open(test_settings.web_base_url)
                login_page.sign_in(username=username, password=password)
                expected_url = (
                    f"{test_settings.web_base_url}{ROLE_START_PATHS[role]}"
                )
                expect(
                    page,
                    f"[storage_state:{role}] после служебного входа ожидали "
                    f"точный адрес {expected_url}",
                ).to_have_url(expected_url)

                cached_states[role] = context.storage_state()
                return cached_states[role]
            finally:
                context.close()

    return get_storage_state


def _artifact_directory(node_id: str) -> Path:
    safe_node_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", node_id).strip("-")
    return Path("test-results") / safe_node_id


@pytest.fixture
def authorized_page_factory(
    browser: Browser,
    browser_context_args: dict[str, object],
    request: pytest.FixtureRequest,
    role_storage_state: RoleStorageStateProvider,
) -> Generator[AuthorizedPageFactory, None, None]:
    """
    Для каждого теста создаёт новый контекст из session storage_state роли.

    Trace и screenshot сохраняются только при падении теста.
    """
    opened_contexts: list[tuple[BrowserContext, Page]] = []

    def create_authorized_page(role: str) -> Page:
        context = browser.new_context(
            **browser_context_args,
            storage_state=role_storage_state(role),
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()
        opened_contexts.append((context, page))
        return page

    yield create_authorized_page

    call_report = getattr(request.node, "rep_call", None)
    test_failed = bool(call_report and call_report.failed)
    artifact_directory = _artifact_directory(request.node.nodeid)

    for context, page in opened_contexts:
        if test_failed:
            artifact_directory.mkdir(parents=True, exist_ok=True)
            if not page.is_closed():
                page.screenshot(
                    path=artifact_directory / "test-failed-1.png",
                    full_page=True,
                )
            context.tracing.stop(path=artifact_directory / "trace.zip")
        else:
            context.tracing.stop()
        context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> Generator[None, Any, None]:
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
