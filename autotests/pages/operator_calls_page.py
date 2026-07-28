from __future__ import annotations

from playwright.sync_api import Page


class OperatorCallsPage:
    def __init__(self, page: Page) -> None:
        self.main_content = page.get_by_role("table")
        self.menu_links = {
            name: page.get_by_role("link", name=name, exact=True)
            for name in (
                "Рабочий стол",
                "Режим звонков",
                "Звонки",
                "Рабочее время",
            )
        }
