from __future__ import annotations

from playwright.sync_api import Locator, Page


class CallTranscriptPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role(
            "heading",
            name="Транскрипт звонка",
            exact=True,
        )

    def detail_value(self, label: str) -> Locator:
        return self.page.get_by_text(
            label,
            exact=True,
        ).locator("xpath=following-sibling::*[1]")
