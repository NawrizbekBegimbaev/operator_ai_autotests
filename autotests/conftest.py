from __future__ import annotations

from collections.abc import Generator

import pytest
from playwright.sync_api import Page

from autotests.config import ConfigurationError, Settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    try:
        return Settings.from_env()
    except ConfigurationError as error:
        raise pytest.UsageError(str(error)) from error


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
