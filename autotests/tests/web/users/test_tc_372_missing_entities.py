from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

from autotests.config import Settings
from autotests.pages.missing_entity_page import MissingEntityPage


AuthorizedPageFactory = Callable[[str], Page]


@dataclass(frozen=True)
class MissingEntityRoute:
    name: str
    role: str
    route_template: str
    api_template: str
    heading: str | None


ROUTES = (
    MissingEntityRoute(
        name="operator",
        role="rop",
        route_template="/dashboard/operators/{id}",
        api_template="/v1/users/{id}",
        heading="Operator",
    ),
    MissingEntityRoute(
        name="call-deal",
        role="rop",
        route_template="/dashboard/calls/{id}",
        api_template="/v1/amocrm/deals/{id}",
        heading="Сделка звонка",
    ),
    MissingEntityRoute(
        name="field",
        role="operator",
        route_template="/dashboard/calls/fields/{id}",
        api_template="/v1/amocrm/fields/{id}",
        heading="Детали поля",
    ),
    MissingEntityRoute(
        name="lead",
        role="superadmin",
        route_template="/dashboard/leads/{id}",
        api_template="/v1/leads/{id}",
        heading=None,
    ),
)


def _role_is_configured(settings: Settings, role: str) -> bool:
    credentials = {
        "rop": (settings.rop_username, settings.rop_password),
        "operator": (settings.operator_username, settings.operator_password),
        "superadmin": (
            settings.superadmin_username,
            settings.superadmin_password,
        ),
    }[role]
    return all(credentials)


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.serial
@pytest.mark.parametrize(
    "route",
    [pytest.param(route, id=route.name) for route in ROUTES],
)
def test_tc_372_missing_entity_has_safe_error_state(
    route: MissingEntityRoute,
    authorized_page_factory: AuthorizedPageFactory,
    test_settings: Settings,
) -> None:
    """TC-372 — старая ссылка даёт 404-state без белого экрана."""
    if not _role_is_configured(test_settings, route.role):
        pytest.skip(
            f"[TC-372:{route.name}] роль {route.role} не настроена в .env"
        )

    missing_id = str(uuid4())
    route_path = route.route_template.format(id=missing_id)
    api_path = route.api_template.format(id=missing_id)
    page = authorized_page_factory(route.role)
    page_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    missing = MissingEntityPage(page)

    response = missing.open(
        test_settings.web_base_url,
        route_path=route_path,
        api_path=api_path,
    )
    assert response.status == 404, (
        f"[TC-372:{route.name}] несуществующий UUID должен вернуть 404, "
        f"получили {response.status}: {response.text()}"
    )
    expect(page).to_have_url(f"{test_settings.web_base_url}{route_path}")
    if route.heading:
        expect(missing.heading(route.heading)).to_be_visible()
    expect(
        missing.back_link,
        f"[TC-372:{route.name}] ожидали доступную ссылку «Назад»",
    ).to_be_visible()
    expect(
        missing.alerts.first,
        f"[TC-372:{route.name}] ожидали видимое состояние ошибки",
    ).to_be_visible()
    alert_text = missing.alerts.first.inner_text().strip()
    assert re.search(
        r"(не удалось|не найден|topilmadi|not found|404)",
        alert_text,
        re.IGNORECASE,
    ), (
        f"[TC-372:{route.name}] сообщение не объясняет отсутствие сущности: "
        f"{alert_text!r}"
    )
    assert not page_errors, (
        f"[TC-372:{route.name}] страница выбросила необработанные ошибки: "
        f"{page_errors!r}"
    )
