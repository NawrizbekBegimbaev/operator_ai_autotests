from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin

import pytest
from playwright.sync_api import APIResponse, expect

from autotests.config import Settings
from autotests.pages.foreign_operator_access_page import (
    ForeignOperatorAccessPage,
)
from autotests.tests.api.rbac.test_tc_032_rop_tenant_isolation import (
    RopTenant,
    tc032_tenants,
)


@dataclass(frozen=True)
class ForeignOperatorRoute:
    suffix: str
    heading_attribute: str
    data_attribute: str


FOREIGN_OPERATOR_ROUTES = (
    ForeignOperatorRoute(
        suffix="",
        heading_attribute="operator_heading",
        data_attribute="salary_input",
    ),
    ForeignOperatorRoute(
        suffix="/calls",
        heading_attribute="calls_heading",
        data_attribute="calls_table",
    ),
)


def _assert_forbidden_user_response(
    response: APIResponse,
    *,
    route_path: str,
) -> None:
    assert response.status == 403, (
        f"[TC-033] на {route_path} ожидали 403 от API чужого оператора, "
        f"получили {response.status}: {response.text()}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        f"[TC-033] на {route_path} ожидали JSON-объект ошибки, "
        f"получили {body!r}"
    )
    assert body.get("status") == 403, (
        f"[TC-033] на {route_path} ожидали status=403, "
        f"получили {body.get('status')!r}: {body!r}"
    )
    assert body.get("title") == "Forbidden", (
        f"[TC-033] на {route_path} ожидали title='Forbidden', "
        f"получили {body.get('title')!r}: {body!r}"
    )
    assert body.get("detail") == "ruxsat yo'q", (
        f"[TC-033] на {route_path} ожидали detail=\"ruxsat yo'q\", "
        f"получили {body.get('detail')!r}: {body!r}"
    )


@pytest.mark.web
@pytest.mark.api
@pytest.mark.critical
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
def test_tc_033_rop_cannot_open_foreign_operator_by_direct_url(
    tc032_tenants: tuple[RopTenant, RopTenant],
    test_settings: Settings,
) -> None:
    """
    TC-033 / TC-042 — РОП-А не открывает карточку и API-данные
    оператора РОП-Б.

    Ожидаемый результат TC-033: на обоих прямых URL остаётся только
    каркас целевой страницы, а имя, username, телефон, зарплата и таблица
    звонков чужого оператора отсутствуют.

    Ожидаемый результат TC-042: GET /v1/users/{id} чужого оператора
    отвечает точным 403 Forbidden / «ruxsat yo'q» и не возвращает его
    данные.
    """
    tenant_a, tenant_b = tc032_tenants
    page = tenant_a.api.page
    access_token = tenant_a.api.authorization_token
    foreign_operator_page = ForeignOperatorAccessPage(
        page,
        foreign_operator=tenant_b.operator,
    )
    foreign_operator_page.authorize_as_rop(
        access_token=access_token,
        rop_user=tenant_a.rop,
    )

    for route in FOREIGN_OPERATOR_ROUTES:
        route_path = (
            f"/dashboard/operators/{tenant_b.operator['id']}{route.suffix}"
        )
        response = foreign_operator_page.open_operator_route(
            base_url=test_settings.web_base_url,
            operator_id=tenant_b.operator["id"],
            suffix=route.suffix,
        )

        _assert_forbidden_user_response(
            response,
            route_path=route_path,
        )
        expect(
            page,
            f"[TC-033] после запроса чужого оператора ожидали URL {route_path}",
        ).to_have_url(
            urljoin(
                f"{test_settings.web_base_url}/",
                route_path.lstrip("/"),
            )
        )
        expect(
            getattr(foreign_operator_page, route.heading_attribute),
            f"[TC-033] на {route_path} ожидали каркас целевой страницы",
        ).to_be_visible()
        expect(
            getattr(foreign_operator_page, route.data_attribute),
            f"[TC-033] на {route_path} данные чужого оператора "
            "не должны отображаться",
        ).to_have_count(0)

        for description, locator in (
            ("username", foreign_operator_page.foreign_username),
            ("имя", foreign_operator_page.foreign_full_name),
            ("телефон", foreign_operator_page.foreign_phone),
        ):
            expect(
                locator,
                f"[TC-033] на {route_path} чужой {description} "
                "не должен отображаться",
            ).to_have_count(0)
