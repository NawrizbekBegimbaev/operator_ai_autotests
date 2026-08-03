from __future__ import annotations

from urllib.parse import urljoin

from playwright.sync_api import Locator, Page


class PlansPage:
    PATH = "/dashboard/plans"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.heading = page.get_by_role(
            "heading",
            name="Тарифы",
            exact=True,
        )
        self.cards = page.locator(".MuiCard-root")

    def open(self, base_url: str) -> None:
        self.page.goto(
            urljoin(f"{base_url}/", self.PATH.lstrip("/")),
            wait_until="commit",
        )

    def card_by_name(self, plan_name: str) -> Locator:
        return self.page.locator(".MuiCard-root").filter(
            has=self.page.get_by_role(
                "heading",
                name=plan_name,
                exact=True,
            )
        )

    def open_edit_dialog(self, plan_name: str) -> PlanEditDialog:
        card = self.card_by_name(plan_name)
        card.get_by_role("button", name="Редактировать", exact=True).click()
        return PlanEditDialog(self.page, plan_name=plan_name)


class PlanEditDialog:
    def __init__(self, page: Page, *, plan_name: str) -> None:
        self.dialog = page.get_by_role(
            "dialog",
            name=f"{plan_name} — редактирование",
            exact=True,
        )
        self.name_input = self.dialog.get_by_label(
            "Название тарифа",
            exact=True,
        )
        self.price_input = self.dialog.get_by_label(
            "Цена (сум/мес) — 0 = «Договорная»",
            exact=True,
        )
        self.description_input = self.dialog.get_by_label(
            "Краткое описание",
            exact=True,
        )
        self.features_input = self.dialog.get_by_label(
            "Возможности (каждую с новой строки)",
            exact=True,
        )
        self.active_switch = self.dialog.get_by_role(
            "checkbox",
            name="Показывать на лендинге",
            exact=True,
        )
        self.save_button = self.dialog.get_by_role(
            "button",
            name="Сохранить",
            exact=True,
        )
        self.cancel_button = self.dialog.get_by_role(
            "button",
            name="Отмена",
            exact=True,
        )
