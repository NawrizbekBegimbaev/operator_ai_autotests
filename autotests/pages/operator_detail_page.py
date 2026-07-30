from __future__ import annotations

import re
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page


class OperatorDetailPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, base_url: str, operator_id: str) -> None:
        path = f"/dashboard/operators/{operator_id}"
        self.page.goto(
            urljoin(f"{base_url}/", path.lstrip("/")),
            wait_until="commit",
        )

    def operator_heading(self, full_name: str) -> Locator:
        return self.page.get_by_role(
            "heading",
            name=full_name,
            exact=True,
        )

    def pipeline_label(self, pipeline_name: str) -> Locator:
        return self.page.get_by_text(
            f"Воронка: {pipeline_name}",
            exact=True,
        )

    def profile_text(self, text: str) -> Locator:
        return self.page.get_by_text(text, exact=False).first

    @property
    def presence_label(self) -> Locator:
        return self.page.get_by_text(
            re.compile(r"^(Онлайн|Оффлайн)$")
        ).first

    def account_action(self, is_active: bool) -> Locator:
        return self.page.get_by_role(
            "button",
            name="Деактивация" if is_active else "Активировать",
            exact=True,
        )

    @property
    def call_recordings_card(self) -> Locator:
        heading = self.page.get_by_role(
            "heading",
            name="Записи звонков",
            exact=True,
        )
        return heading.locator(
            "xpath=ancestor::div[contains(@class, 'MuiCard-root')][1]"
        )

    def call_title(self, index: int) -> Locator:
        return self.call_recordings_card.locator(
            ".MuiTypography-subtitle2"
        ).nth(index)

    def audio_button(self, index: int = 0) -> Locator:
        return self.audio_element(index).locator("xpath=..").locator(
            "button"
        ).first

    def audio_element(self, index: int = 0) -> Locator:
        return self.call_recordings_card.locator("audio").nth(index)
