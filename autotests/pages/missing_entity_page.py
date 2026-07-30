from __future__ import annotations

import re
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import APIResponse, Locator, Page


class MissingEntityPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.alerts = page.get_by_role("alert")
        self.back_link = page.get_by_role(
            "link",
            name=re.compile(r"^(Назад|Orqaga)$"),
        )

    def open(
        self,
        base_url: str,
        *,
        route_path: str,
        api_path: str,
    ) -> APIResponse:
        with self.page.expect_response(
            lambda response: (
                response.request.method == "GET"
                and urlsplit(response.url).path == api_path
            )
        ) as response_info:
            self.page.goto(
                urljoin(f"{base_url}/", route_path.lstrip("/")),
                wait_until="commit",
            )
        return response_info.value

    def heading(self, name: str) -> Locator:
        return self.page.get_by_role(
            "heading",
            name=name,
            exact=True,
        )
