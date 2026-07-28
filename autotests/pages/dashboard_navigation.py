from __future__ import annotations

from playwright.sync_api import Locator, Page


class DashboardNavigation:
    """Левое меню авторизованной панели."""

    def __init__(self, page: Page, menu_names: tuple[str, ...]) -> None:
        self.page = page
        self.links: dict[str, Locator] = {
            name: page.get_by_role("link", name=name, exact=True)
            for name in menu_names
        }

    def open_start_page(self, base_url: str) -> None:
        self.page.goto(base_url)
