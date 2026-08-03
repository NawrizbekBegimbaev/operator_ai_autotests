from __future__ import annotations

from autotests.api.user_api import UserApi


def cleanup_rops_by_username(
    superadmin_api: UserApi,
    username: str,
    *,
    checkpoint: str,
) -> None:
    response = superadmin_api.list_users_by_username(username)
    assert response.status == 200, (
        f"{checkpoint} при поиске тестового РОП ожидали 200, получили "
        f"{response.status}: {response.text()}"
    )
    body = response.json()
    assert isinstance(body, dict), (
        f"{checkpoint} ожидали JSON-объект списка, получили {body!r}"
    )
    items = body.get("items")
    assert isinstance(items, list), (
        f"{checkpoint} ожидали массив items, получили {body!r}"
    )

    for item in items:
        assert isinstance(item, dict), (
            f"{checkpoint} ожидали объект пользователя, получили {item!r}"
        )
        user_id = item.get("id")
        assert isinstance(user_id, str) and user_id, (
            f"{checkpoint} у пользователя нет id: {item!r}"
        )
        delete_response = superadmin_api.delete_user(user_id)
        assert delete_response.status == 200, (
            f"{checkpoint} при удалении тестового РОП ожидали 200, "
            f"получили {delete_response.status}: {delete_response.text()}"
        )
        delete_body = delete_response.json()
        assert delete_body.get("message") == "o'chirildi", (
            f'{checkpoint} ожидали message="o\'chirildi", получили '
            f"{delete_body!r}"
        )
