from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Page


class LoginPage:
    SIGN_IN_PATH = "/auth/jwt/sign-in"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username_input = page.get_by_label("Логин", exact=True)
        self.password_input = page.get_by_label("Пароль", exact=True)
        self.submit_button = page.get_by_role("button", name="Войти", exact=True)

    def open(self, base_url: str) -> None:
        self.page.goto(urljoin(f"{base_url}/", self.SIGN_IN_PATH))

    def sign_in(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()
