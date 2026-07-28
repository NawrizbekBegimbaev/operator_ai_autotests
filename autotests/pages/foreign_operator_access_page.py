from __future__ import annotations

import json
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import APIResponse, Page


class ForeignOperatorAccessPage:
    """Прямой доступ РОП к карточке чужого оператора и его звонкам."""

    JWT_STORAGE_KEY = "jwt_access_token"
    USER_STORAGE_KEY = "jwt_user"

    def __init__(
        self,
        page: Page,
        *,
        foreign_operator: dict[str, object],
    ) -> None:
        self.page = page
        self.foreign_operator = foreign_operator

        self.operator_heading = page.get_by_role(
            "heading",
            name="Operator",
            exact=True,
        )
        self.calls_heading = page.get_by_role(
            "heading",
            name="Звонки оператора",
            exact=True,
        )
        self.foreign_username = page.get_by_text(
            str(foreign_operator["username"]),
            exact=True,
        )
        self.foreign_full_name = page.get_by_text(
            (
                f"{foreign_operator['first_name']} "
                f"{foreign_operator['last_name']}"
            ),
            exact=True,
        )
        self.foreign_phone = page.get_by_text(
            str(foreign_operator["phone"]),
            exact=True,
        )
        self.salary_input = page.get_by_label(
            "Зарплата",
            exact=True,
        )
        self.calls_table = page.get_by_role("table")

    def authorize_as_rop(
        self,
        *,
        access_token: str,
        rop_user: dict[str, object],
    ) -> None:
        self.page.evaluate(
            """([tokenKey, userKey, token, user]) => {
                window.localStorage.setItem(tokenKey, token);
                window.localStorage.setItem(userKey, user);
            }""",
            [
                self.JWT_STORAGE_KEY,
                self.USER_STORAGE_KEY,
                access_token,
                json.dumps(rop_user, ensure_ascii=False),
            ],
        )

    def open_operator_route(
        self,
        *,
        base_url: str,
        operator_id: str,
        suffix: str,
    ) -> APIResponse:
        user_api_path = f"/v1/users/{operator_id}"
        route_path = f"/dashboard/operators/{operator_id}{suffix}"

        with self.page.expect_response(
            lambda response: (
                response.request.method == "GET"
                and urlsplit(response.url).path == user_api_path
            )
        ) as response_info:
            self.page.goto(
                urljoin(f"{base_url}/", route_path.lstrip("/")),
                wait_until="commit",
            )

        return response_info.value
