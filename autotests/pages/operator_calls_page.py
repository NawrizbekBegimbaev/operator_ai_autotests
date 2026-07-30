from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Locator, Page


class OperatorCallsPage:
    def __init__(self, page: Page) -> None:
        self.page = page
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

    def open_for_operator(self, base_url: str, operator_id: str) -> None:
        path = f"/dashboard/operators/{operator_id}/calls"
        self.page.goto(
            urljoin(f"{base_url}/", path.lstrip("/")),
            wait_until="commit",
        )

    def heading(self, full_name: str) -> Locator:
        return self.page.get_by_role(
            "heading",
            name=f"{full_name} qo'ng'iroqlari",
            exact=True,
        )

    @property
    def data_rows(self) -> Locator:
        return self.main_content.locator("tbody tr")

    def row_cells(self, index: int) -> Locator:
        return self.data_rows.nth(index).get_by_role("cell")
