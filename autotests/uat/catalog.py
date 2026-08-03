from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "qa-docs/daily-uat-checklist.json"


class UATCatalogError(RuntimeError):
    """Структурированный UAT-чеклист нарушает обязательный контракт."""


@dataclass(frozen=True)
class UATCase:
    id: str
    role: str
    layer: str
    screen: str
    scenario: str
    expected_result: str
    priority: str
    estimated_seconds: int
    execution_state: str
    automation_state: str
    source_cases: tuple[str, ...]
    steps: tuple[str, ...]
    cleanup: str
    blocked_by: tuple[str, ...] = ()
    activation_gate: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "UATCase":
        required = {
            "id",
            "role",
            "layer",
            "screen",
            "scenario",
            "expected_result",
            "priority",
            "estimated_seconds",
            "execution_state",
            "automation_state",
            "source_cases",
            "steps",
            "cleanup",
        }
        missing = sorted(required - raw.keys())
        if missing:
            raise UATCatalogError(
                f"UAT-кейс {raw.get('id', '<без ID>')} не содержит: {missing}."
            )
        case = cls(
            id=str(raw["id"]),
            role=str(raw["role"]),
            layer=str(raw["layer"]),
            screen=str(raw["screen"]),
            scenario=str(raw["scenario"]),
            expected_result=str(raw["expected_result"]),
            priority=str(raw["priority"]),
            estimated_seconds=int(raw["estimated_seconds"]),
            execution_state=str(raw["execution_state"]),
            automation_state=str(raw["automation_state"]),
            source_cases=tuple(str(value) for value in raw["source_cases"]),
            steps=tuple(str(value) for value in raw["steps"]),
            cleanup=str(raw["cleanup"]),
            blocked_by=tuple(str(value) for value in raw.get("blocked_by", [])),
            activation_gate=str(raw.get("activation_gate", "")),
        )
        if not case.id.startswith("UAT-"):
            raise UATCatalogError(f"Некорректный UAT-ID: {case.id!r}.")
        if case.priority not in {"P0", "P1", "P2"}:
            raise UATCatalogError(
                f"{case.id}: неизвестный приоритет {case.priority!r}."
            )
        if case.layer not in {"ui", "api", "hybrid_ui_api"}:
            raise UATCatalogError(
                f"{case.id}: неизвестный уровень {case.layer!r}."
            )
        if case.execution_state not in {"planned", "blocked_defect"}:
            raise UATCatalogError(
                f"{case.id}: неизвестный execution_state "
                f"{case.execution_state!r}."
            )
        if case.execution_state == "blocked_defect" and not case.blocked_by:
            raise UATCatalogError(
                f"{case.id}: blocked_defect должен ссылаться на BUG-ID."
            )
        return case


@dataclass(frozen=True)
class UATCatalog:
    status: str
    cases: tuple[UATCase, ...]

    @property
    def by_id(self) -> dict[str, UATCase]:
        return {case.id: case for case in self.cases}


def load_catalog(path: Path = DEFAULT_CATALOG_PATH) -> UATCatalog:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise UATCatalogError(f"Не удалось прочитать {path}: {error}") from error
    if not isinstance(raw, dict) or not isinstance(raw.get("scenarios"), list):
        raise UATCatalogError(f"{path}: отсутствует массив scenarios.")
    cases = tuple(UATCase.from_dict(item) for item in raw["scenarios"])
    ids = [case.id for case in cases]
    if len(ids) != len(set(ids)):
        raise UATCatalogError("В UAT-чеклисте обнаружены повторяющиеся ID.")
    budget = raw.get("budget")
    if not isinstance(budget, dict) or budget.get("total_scenarios") != len(cases):
        raise UATCatalogError(
            "budget.total_scenarios не совпадает с числом scenarios."
        )
    return UATCatalog(status=str(raw.get("status", "")), cases=cases)
