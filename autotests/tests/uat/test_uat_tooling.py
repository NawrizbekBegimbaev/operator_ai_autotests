from __future__ import annotations

from pathlib import Path

from autotests.uat.report import build_report, render_human_report
from autotests.uat.telegram import split_message


def test_uat_report_keeps_three_header_numbers_and_hides_traceback(
    tmp_path: Path,
) -> None:
    junit = tmp_path / "junit.xml"
    junit.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="uat" tests="2">
  <testcase name="test[UAT-SYS-001]" time="1.2">
    <properties><property name="uat_id" value="UAT-SYS-001"/></properties>
  </testcase>
  <testcase name="test[UAT-SYS-002]" time="0.3">
    <properties><property name="uat_id" value="UAT-SYS-002"/></properties>
    <failure message="Форма входа не видна">SECRET TRACEBACK</failure>
  </testcase>
</testsuite></testsuites>
""",
        encoding="utf-8",
    )
    report = build_report(junit, pytest_returncode=1)
    text = render_human_report(report)
    assert report.passed == 1
    assert report.launched == 2
    assert report.not_ready == 24
    assert report.checkable == 26
    assert report.blocked_defect == 7
    assert report.total == 33
    assert "Пройдено: 1 из 2 запущенных" in text
    assert "24 не готово к запуску" in text
    assert "7 заблокировано дефектом" in text
    assert "всего в чеклисте: 33" in text
    assert "Форма входа не видна" in text
    assert "SECRET TRACEBACK" not in text


def test_telegram_split_preserves_report_and_limits_chunks() -> None:
    report = "\n".join(f"UAT line {index}: " + "x" * 100 for index in range(100))
    chunks = split_message(report, limit=500)
    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)
    assert "\n".join(chunks) == report
