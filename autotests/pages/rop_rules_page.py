from __future__ import annotations

from playwright.sync_api import Page


class RopRulesPage:
    def __init__(self, page: Page) -> None:
        self.main_content = page.get_by_role(
            "heading",
            name="Статусы лида",
            exact=True,
        )
        self.menu_links = {
            name: page.get_by_role("link", name=name, exact=True)
            for name in (
                "Правила",
                "Операторы",
                "Настройка очереди",
                "Критерии",
                "Посещаемость",
            )
        }
