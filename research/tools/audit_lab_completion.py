"""Verify the completion criterion for the FARMAXIA laboratory foundation."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
LOOP = ROOT / "RESEARCH_LOOP.md"
CORPUS = ROOT / "research" / "corpus" / "manifest.json"
SUITE = ROOT / "research" / "tools" / "run_suite.py"

REQUIRED_EXPERIMENTS = [
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
]

DECISIONS = [
    "008-ketamine-investment.md",
    "012-codeine-general-kill.md",
    "024-vizz-tool-adoption.md",
    "025-codeine-session-state.md",
    "026-xanax-analogy-chain.md",
    "028-xanax-archive.md",
    "032-laboratory-state-audit.md",
    "037-codeine-objective-oracle.md",
    "038-vizz-gaze-quality-gate.md",
    "039-codeine-executable-oracle.md",
    "041-vizz-webgazer-opt-in.md",
]

LITERATURE = [
    "006-neuro-human-computational.md",
    "007-analogy-information-foraging.md",
    "008-vizz-perceptual-adaptation.md",
    "009-substances-and-computing-boundary.md",
    "010-vizz-observability-boundary.md",
    "011-vizz-display-conditions.md",
    "012-codeine-objective-signal.md",
    "013-codeine-verifiable-objective.md",
    "014-vizz-gaze-quality-tools.md",
    "015-codeine-executable-oracle-mutation.md",
    "016-vizz-webgazer-runtime.md",
]


def fail_if(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    loop = LOOP.read_text(encoding="utf-8")
    suite = SUITE.read_text(encoding="utf-8")
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    failures: list[str] = []

    fail_if("python research/tools/run_suite.py" in readme, "reproducibility command is missing", failures)
    fail_if("validate_provenance.py" in suite and "audit_lab_state.py" in suite, "suite does not expose provenance and state audits", failures)
    fail_if("VIZZ" in readme and "CODE-INE" in readme and "X-ANA-X" in readme, "hypothesis inventory is incomplete", failures)

    for experiment in REQUIRED_EXPERIMENTS:
        directory = ROOT / "experiments" / experiment
        fail_if((directory / "README.md").is_file(), f"missing experiment contract: {experiment}", failures)
        fail_if((directory / "provenance.json").is_file(), f"missing experiment provenance: {experiment}", failures)
        fail_if(experiment in suite, f"experiment is not reproducible from suite: {experiment}", failures)

    for decision in DECISIONS:
        fail_if((ROOT / "research" / "decisions" / decision).is_file(), f"missing decision: {decision}", failures)
    for literature in LITERATURE:
        fail_if((ROOT / "research" / "literature" / literature).is_file(), f"missing literature record: {literature}", failures)

    fail_if("archivado como hipótesis independiente" in readme and "X-ANA-X" in loop, "X-ANA-X archive boundary is missing", failures)
    fail_if("KETAMINE" in readme and "en cuarentena" in readme and "QUARANTINED" in loop, "KETAMINE quarantine boundary is missing", failures)
    fail_if(corpus.get("status") == "empty_by_design" and corpus.get("entries") == [], "corpus is not empty by design", failures)
    fail_if("sin datos humanos" in readme and "no se realizan estudios con participantes" in loop, "human-data boundary is missing", failures)
    fail_if("intoxicación" in loop and "pharmacological_inference" in suite, "intoxication/pharmacology boundary is missing", failures)

    prohibited_true = re.compile(r"(?:human_data|raw_capture|devices_started|network_used)\s*['\"]?\s*:\s*true|(?:human_data|raw_capture)\s*=\s*True", re.IGNORECASE)
    for path in (ROOT / "experiments").rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".py"}:
            fail_if(not prohibited_true.search(path.read_text(encoding="utf-8")), f"prohibited true flag in {path.relative_to(ROOT)}", failures)

    active_unknowns = [
        ROOT / "experiments" / "013-vizz-perceptual-adaptation" / "provenance.json",
        ROOT / "experiments" / "016-codeine-session-state" / "provenance.json",
        ROOT / "experiments" / "028-vizz-gaze-quality-gate" / "provenance.json",
        ROOT / "experiments" / "029-codeine-executable-oracle" / "provenance.json",
        ROOT / "experiments" / "030-vizz-webgazer-opt-in" / "provenance.json",
    ]
    for path in active_unknowns:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        fail_if(bool(manifest.get("unknowns")), f"active hypothesis lacks explicit unknowns: {path.relative_to(ROOT)}", failures)

    if failures:
        print("LAB_COMPLETION_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("LAB_COMPLETION_VALID")
    print(f"requirements={len(REQUIRED_EXPERIMENTS) + len(DECISIONS) + len(LITERATURE)}")
    print("vizz=provisional_with_explicit_human_unknowns")
    print("codeine=provisional_with_executable_oracle_and_explicit_human_unknowns")
    print("xanax=archived_as_independent_hypothesis")
    print("ketamine=quarantined")
    print("safety=empty_corpus_no_human_data_no_intoxication")
    print("closure=lab_foundation_criterion_met_not_scientific_claim")


if __name__ == "__main__":
    main()
