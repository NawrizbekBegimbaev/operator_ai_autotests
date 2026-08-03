from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from autotests.uat.catalog import UATCase, UATCatalog, load_catalog


TASHKENT = ZoneInfo("Asia/Tashkent")
UAT_ID_RE = re.compile(r"UAT-[A-Z]+-\d{3}")


@dataclass(frozen=True)
class RawTestResult:
    case_id: str
    state: str
    duration_seconds: float
    reason: str = ""


@dataclass(frozen=True)
class CaseOutcome:
    id: str
    role: str
    scenario: str
    expected_result: str
    priority: str
    state: str
    duration_seconds: float
    reason: str
    blocked_by: tuple[str, ...]


@dataclass(frozen=True)
class RoleOutcome:
    role: str
    passed: int
    checkable: int
    total: int


@dataclass(frozen=True)
class UATReport:
    generated_at: str
    status: str
    passed: int
    checkable: int
    blocked_defect: int
    total: int
    duration_seconds: float
    pytest_returncode: int
    roles: tuple[RoleOutcome, ...]
    outcomes: tuple[CaseOutcome, ...]

    @property
    def is_green(self) -> bool:
        return self.passed == self.checkable and self.pytest_returncode == 0


def _short_reason(value: str, *, limit: int = 220) -> str:
    compact = " ".join(value.replace("\x1b", "").split())
    compact = re.sub(r"^E\s+", "", compact)
    if not compact:
        return "Причина не указана pytest."
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1].rstrip()}…"


def _case_id(testcase: ET.Element) -> str | None:
    properties = testcase.find("properties")
    if properties is not None:
        for prop in properties.findall("property"):
            if prop.get("name") == "uat_id" and prop.get("value"):
                return prop.get("value")
    match = UAT_ID_RE.search(testcase.get("name", ""))
    return match.group(0) if match else None


def parse_junit(path: Path) -> dict[str, RawTestResult]:
    if not path.exists():
        return {}
    root = ET.parse(path).getroot()
    results: dict[str, RawTestResult] = {}
    for testcase in root.iter("testcase"):
        case_id = _case_id(testcase)
        if case_id is None:
            continue
        if case_id in results:
            raise ValueError(f"JUnit содержит повторный результат {case_id}.")
        duration = float(testcase.get("time", "0") or 0)
        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")
        if failure is not None or error is not None:
            node = failure if failure is not None else error
            assert node is not None
            reason = node.get("message") or node.text or "pytest failure"
            state = "failed"
        elif skipped is not None:
            reason = skipped.get("message") or skipped.text or "pytest skip"
            state = "not_run"
        else:
            reason = ""
            state = "passed"
        results[case_id] = RawTestResult(
            case_id=case_id,
            state=state,
            duration_seconds=duration,
            reason=_short_reason(reason),
        )
    return results


def _outcome_for(case: UATCase, raw: RawTestResult | None) -> CaseOutcome:
    if case.execution_state == "blocked_defect":
        return CaseOutcome(
            id=case.id,
            role=case.role,
            scenario=case.scenario,
            expected_result=case.expected_result,
            priority=case.priority,
            state="blocked_defect",
            duration_seconds=raw.duration_seconds if raw else 0,
            reason=f"Подтверждённый дефект: {', '.join(case.blocked_by)}",
            blocked_by=case.blocked_by,
        )
    if raw is None:
        state = "not_run"
        reason = "Тест отсутствует в результате прогона."
        duration = 0
    else:
        state = raw.state
        reason = raw.reason
        duration = raw.duration_seconds
    return CaseOutcome(
        id=case.id,
        role=case.role,
        scenario=case.scenario,
        expected_result=case.expected_result,
        priority=case.priority,
        state=state,
        duration_seconds=duration,
        reason=reason,
        blocked_by=case.blocked_by,
    )


def build_report(
    junit_path: Path,
    *,
    pytest_returncode: int,
    catalog: UATCatalog | None = None,
) -> UATReport:
    active_catalog = catalog or load_catalog()
    raw = parse_junit(junit_path)
    unknown = sorted(set(raw) - set(active_catalog.by_id))
    if unknown:
        raise ValueError(f"JUnit содержит неизвестные UAT-ID: {unknown}.")
    outcomes = tuple(
        _outcome_for(case, raw.get(case.id)) for case in active_catalog.cases
    )
    checkable = sum(item.state != "blocked_defect" for item in outcomes)
    passed = sum(item.state == "passed" for item in outcomes)
    blocked = sum(item.state == "blocked_defect" for item in outcomes)
    grouped: dict[str, list[CaseOutcome]] = defaultdict(list)
    for outcome in outcomes:
        grouped[outcome.role].append(outcome)
    roles = tuple(
        RoleOutcome(
            role=role,
            passed=sum(item.state == "passed" for item in items),
            checkable=sum(item.state != "blocked_defect" for item in items),
            total=len(items),
        )
        for role, items in grouped.items()
    )
    status = "green" if passed == checkable and pytest_returncode == 0 else "red"
    return UATReport(
        generated_at=datetime.now(TASHKENT).isoformat(timespec="seconds"),
        status=status,
        passed=passed,
        checkable=checkable,
        blocked_defect=blocked,
        total=len(outcomes),
        duration_seconds=sum(item.duration_seconds for item in outcomes),
        pytest_returncode=pytest_returncode,
        roles=roles,
        outcomes=outcomes,
    )


def _duration(value: float) -> str:
    seconds = max(0, round(value))
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes} мин {seconds:02d} сек"


def render_human_report(report: UATReport) -> str:
    icon = "🟢" if report.is_green else "🔴"
    lines = [
        f"{icon} Operator AI — ежедневный happy-path UAT",
        (
            f"Пройдено: {report.passed} из {report.checkable} проверяемых "
            f"(ещё {report.blocked_defect} заблокировано дефектом; "
            f"всего в чеклисте: {report.total})"
        ),
        f"Время тестов: {_duration(report.duration_seconds)}",
        "",
        "По ролям:",
    ]
    for role in report.roles:
        lines.append(
            f"• {role.role}: {role.passed}/{role.checkable}/{role.total}"
        )
    problems = [
        item for item in report.outcomes if item.state in {"failed", "not_run"}
    ]
    if problems:
        lines.extend(["", "Требуют внимания:"])
        for item in problems:
            label = "упало" if item.state == "failed" else "не выполнено"
            lines.append(
                f"• {item.id} · {item.role} · {label}: "
                f"{item.scenario}. {_short_reason(item.reason, limit=150)}"
            )
    if report.blocked_defect:
        defects = Counter(
            defect
            for item in report.outcomes
            for defect in item.blocked_by
            if item.state == "blocked_defect"
        )
        lines.extend(
            ["", f"Заблокировано дефектом: {report.blocked_defect} "
             f"({', '.join(sorted(defects))})"]
        )
    return "\n".join(lines)


def write_report_files(report: UATReport, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / "report.txt"
    json_path = output_dir / "summary.json"
    text_path.write_text(render_human_report(report) + "\n", encoding="utf-8")
    payload: dict[str, Any] = asdict(report)
    payload["is_green"] = report.is_green
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return text_path, json_path
