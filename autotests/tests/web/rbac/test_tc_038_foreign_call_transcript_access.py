from __future__ import annotations

import pytest


@pytest.mark.web
@pytest.mark.high
@pytest.mark.negative
@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.manual_setup
def test_tc_038_foreign_call_transcript_is_unavailable() -> None:
    """
    TC-038 — транскрипция чужого звонка недоступна по прямой ссылке.

    Ожидаемый результат: оператор РОП-А не получает текст транскрипции
    звонка компании РОП-Б по прямому URL.
    """
    pytest.skip(
        "TC-038: нужен реальный завершённый звонок второй компании с "
        "готовой транскрипцией и известными call/transcript ID; создать "
        "его через API текущего стенда нельзя."
    )
