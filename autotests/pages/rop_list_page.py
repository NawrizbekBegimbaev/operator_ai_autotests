from __future__ import annotations

import re

from playwright.sync_api import Page


class RopListPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role(
            "heading",
            name=re.compile(r"^Компании РОП · \d+$"),
        )
        self.companies_table = page.get_by_role("table")
        self.rop_menu_link = page.get_by_role("link", name="РОПы", exact=True)
        self.leads_menu_link = page.get_by_role("link", name="Лиды", exact=True)
        self.tariffs_menu_link = page.get_by_role("link", name="Тарифы", exact=True)
