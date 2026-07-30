from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Locator, Page


class OperatorDealsPage:
    PATH = "/dashboard/calls"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role(
            "heading",
            name="Звонки",
            exact=True,
        )
        self.table = page.get_by_role("table")
        self.column_headers = self.table.get_by_role("columnheader")

    def open(self, base_url: str) -> None:
        self.page.goto(
            urljoin(f"{base_url}/", self.PATH.lstrip("/")),
            wait_until="commit",
        )

    @property
    def data_rows(self) -> Locator:
        return self.table.locator("tbody tr")

    def row_cells(self, index: int) -> Locator:
        return self.data_rows.nth(index).get_by_role("cell")


class OperatorDealDetailsPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role(
            "heading",
            name="Сделка звонка",
            exact=True,
        )
        self.deal_data_heading = page.get_by_role(
            "heading",
            name="Данные сделки",
            exact=True,
        )
        self.back_button = page.get_by_role(
            "link",
            name="Назад",
            exact=True,
        )
