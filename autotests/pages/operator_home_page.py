from __future__ import annotations

from playwright.sync_api import Page


class OperatorHomePage:
    def __init__(self, page: Page) -> None:
        self.main_content = page.get_by_role(
            "heading",
            name="Последние звонки",
            exact=True,
        )
        self.start_call_button = page.get_by_role(
            "button",
            name="Начать звонок",
        )
        self.content_elements = {
            "блок «Последние звонки»": self.main_content,
            "кнопку «Начать звонок»": self.start_call_button,
        }
        self.menu_links = {
            name: page.get_by_role("link", name=name, exact=True)
            for name in (
                "Рабочий стол",
                "Режим звонков",
                "Звонки",
                "Рабочее время",
            )
        }
