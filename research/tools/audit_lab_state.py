"""Audit the consolidated FARMAXIA lab state without collecting data."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
LOOP = ROOT / "RESEARCH_LOOP.md"
CORPUS = ROOT / "research" / "corpus" / "manifest.json"
SUITE = ROOT / "research" / "tools" / "run_suite.py"


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    loop = LOOP.read_text(encoding="utf-8")
    suite = SUITE.read_text(encoding="utf-8")
    failures: list[str] = []

    check("descriptor provisional" in readme and "operador independiente eliminado" in readme, "CODE-INE status is not explicit", failures)
    check("archivado como hipótesis independiente" in readme, "X-ANA-X archive is not explicit", failures)
    check("en cuarentena" in readme and "KETAMINE" in readme, "KETAMINE quarantine is not explicit", failures)
    check("sin datos humanos" in readme, "VIZZ human-data limit is missing", failures)
    check("UNASSIGNED / QUARANTINED" in loop, "loop quarantine contract is missing", failures)
    check("X-ANA-X" in loop and "archiva" in loop, "loop archive record is missing", failures)
    check((ROOT / "research" / "literature" / "010-vizz-observability-boundary.md").is_file(), "observability literature record is missing", failures)
    check((ROOT / "research" / "literature" / "011-vizz-display-conditions.md").is_file(), "display condition literature record is missing", failures)
    check((ROOT / "research" / "literature" / "012-codeine-objective-signal.md").is_file(), "objective signal literature record is missing", failures)
    check((ROOT / "research" / "literature" / "013-codeine-verifiable-objective.md").is_file(), "verifiable objective literature record is missing", failures)
    check((ROOT / "research" / "literature" / "014-vizz-gaze-quality-tools.md").is_file(), "gaze quality literature record is missing", failures)
    check((ROOT / "research" / "literature" / "015-codeine-executable-oracle-mutation.md").is_file(), "executable oracle literature record is missing", failures)

    required_experiments = [
        "013-vizz-perceptual-adaptation",
        "014-vizz-decision-query",
        "015-vizz-session-contract",
        "016-codeine-session-state",
        "017-xanax-analogy-chain",
        "018-xanax-reformulation-control",
        "019-xanax-provenance-archive-audit",
        "020-vizz-codeine-event-bridge",
        "021-manual-adapter-gate",
        "022-vizz-codeine-long-bridge",
        "023-vizz-codeine-observability-boundary",
        "024-vizz-latency-coverage-boundary",
        "025-vizz-display-condition-invariance",
        "026-codeine-objective-signal",
        "027-codeine-objective-oracle",
        "028-vizz-gaze-quality-gate",
        "029-codeine-executable-oracle",
        "030-vizz-webgazer-opt-in",
        "060-codeine-experience-compiler",
    ]
    for experiment in required_experiments:
        directory = ROOT / "experiments" / experiment
        check((directory / "README.md").is_file(), f"missing README for {experiment}", failures)
        check((directory / "provenance.json").is_file(), f"missing provenance for {experiment}", failures)
        check(experiment in suite, f"{experiment} is not integrated into suite", failures)

    decisions = [
        "028-xanax-archive.md",
        "029-vizz-codeine-bridge.md",
        "030-manual-adapter-gate.md",
        "031-long-vizz-codeine-bridge.md",
        "033-vizz-codeine-observability-boundary.md",
        "034-vizz-latency-coverage-boundary.md",
        "035-vizz-display-condition-invariance.md",
        "036-codeine-objective-signal.md",
        "037-codeine-objective-oracle.md",
        "038-vizz-gaze-quality-gate.md",
        "039-codeine-executable-oracle.md",
        "040-laboratory-completion-audit.md",
        "041-vizz-webgazer-opt-in.md",
        "066-codeine-experience-compiler.md",
    ]
    for decision in decisions:
        check((ROOT / "research" / "decisions" / decision).is_file(), f"missing current decision {decision}", failures)

    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    check(corpus.get("status") == "empty_by_design" and corpus.get("entries") == [], "corpus is not empty by design", failures)

    prohibited_true = re.compile(r"(?:human_data|raw_capture|devices_started|network_used)\s*['\"]?\s*:\s*true|(?:human_data|raw_capture)\s*=\s*True", re.IGNORECASE)
    for path in (ROOT / "experiments").rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".py"}:
            check(not prohibited_true.search(path.read_text(encoding="utf-8")), f"prohibited true flag in {path.relative_to(ROOT)}", failures)

    check("manual_event_adapter.py" in suite or (ROOT / "research" / "tools" / "manual_event_adapter.py").is_file(), "manual adapter is missing", failures)
    if failures:
        print("LAB_STATE_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("LAB_STATE_VALID")
    print("active_fronts=VIZZ,CODE-INE")
    print("xanax=archived")
    print("ketamine=quarantined")
    print("corpus=empty_by_design")
    print("human_data=absent")


if __name__ == "__main__":
    main()
