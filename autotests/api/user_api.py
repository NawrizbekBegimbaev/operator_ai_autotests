from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

from playwright.sync_api import APIResponse, Page


class UserApi:
    """Запросы к API пользователей от имени уже авторизованной роли."""

    JWT_STORAGE_KEY = "jwt_access_token"
    USERS_PATH = "/v1/users"

    def __init__(
        self,
        page: Page,
        api_base_url: str,
        access_token: str,
    ) -> None:
        self.page = page
        self.api_base_url = api_base_url
        self._authorization_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_authorized_page(
        cls,
        page: Page,
        web_base_url: str,
        discovery_path: str,
    ) -> UserApi:
        with page.expect_response(
            lambda response: (
                response.request.method == "GET"
                and urlsplit(response.url).path == cls.USERS_PATH
            )
        ) as users_response_info:
            page.goto(
                urljoin(
                    f"{web_base_url}/",
                    discovery_path.lstrip("/"),
                )
            )

        users_response_url = urlsplit(users_response_info.value.url)
        api_base_url = urlunsplit(
            (
                users_response_url.scheme,
                users_response_url.netloc,
                "",
                "",
                "",
            )
        )
        access_token = page.evaluate(
            "(storageKey) => window.localStorage.getItem(storageKey)",
            cls.JWT_STORAGE_KEY,
        )
        if not isinstance(access_token, str) or not access_token:
            raise RuntimeError(
                "В авторизованном storage_state отсутствует access token."
            )

        return cls(
            page=page,
            api_base_url=api_base_url,
            access_token=access_token,
        )

    def list_users_by_username(self, username: str) -> APIResponse:
        if "'" in username:
            raise ValueError(
                "Имя пользователя с апострофом нельзя безопасно подставить "
                "в API-фильтр."
            )
        return self.page.request.get(
            self._url(self.USERS_PATH),
            params={
                "filter": f"username='{username}'",
                "page": 1,
                "perPage": 100,
            },
            headers=self._authorization_headers,
        )

    def get_user(self, user_id: str) -> APIResponse:
        return self.page.request.get(
            self._url(f"{self.USERS_PATH}/{user_id}"),
            headers=self._authorization_headers,
        )

    def create_operator(self, payload: Mapping[str, Any]) -> APIResponse:
        return self.page.request.post(
            self._url("/v1/operators"),
            data=dict(payload),
            headers=self._authorization_headers,
        )

    def patch_user(
        self,
        user_id: str,
        payload: Mapping[str, Any],
    ) -> APIResponse:
        return self.page.request.patch(
            self._url(f"{self.USERS_PATH}/{user_id}"),
            data=dict(payload),
            headers=self._authorization_headers,
        )

    def delete_user(self, user_id: str) -> APIResponse:
        return self.page.request.delete(
            self._url(f"{self.USERS_PATH}/{user_id}"),
            headers=self._authorization_headers,
        )

    def _url(self, path: str) -> str:
        return urljoin(f"{self.api_base_url}/", path.lstrip("/"))
