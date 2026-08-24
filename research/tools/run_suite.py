"""Run the reproducible FARMAKSIA research suite with standard-library tools."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable


def command(label: str, args: list[str], expected: str | None = None) -> None:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = f"{completed.stdout}\n{completed.stderr}".strip()
    if completed.returncode != 0:
        raise RuntimeError(f"{label} failed with {completed.returncode}: {output[-2000:]}")
    if expected is not None and expected not in output:
        raise RuntimeError(f"{label} did not emit {expected!r}: {output[-2000:]}")
    print(f"PASS {label}")


def python_script(path: str, *arguments: str) -> list[str]:
    return [PYTHON, str(ROOT / path), *arguments]


def main() -> None:
    provenance = [
        "experiments/001-representation-boundary/provenance.json",
        "experiments/002-continuation-boundary/provenance.json",
        "experiments/003-vizz-decision/provenance.json",
        "experiments/004-ketamine-investment/provenance.json",
        "experiments/005-composition-boundary/provenance.json",
        "experiments/006-invariant-ladder/provenance.json",
        "experiments/007-codeine-general-boundary/provenance.json",
        "experiments/008-xanax-boundary/provenance.json",
        "experiments/009-vizz-counterbalanced/provenance.json",
        "experiments/010-metamorphic-boundary/provenance.json",
        "experiments/011-nonrectangular-boundary/provenance.json",
        "experiments/012-curves-layers-boundary/provenance.json",
        "experiments/013-vizz-perceptual-adaptation/provenance.json",
        "experiments/014-vizz-decision-query/provenance.json",
        "experiments/015-vizz-session-contract/provenance.json",
        "experiments/016-codeine-session-state/provenance.json",
        "experiments/017-xanax-analogy-chain/provenance.json",
    ]

    command("compile Python", [PYTHON, "-m", "compileall", "-q", "research", "experiments"])
    command("validate empty corpus manifest", python_script("research/tools/validate_corpus_manifest.py"), "CORPUS_VALID")
    command("experiment 001", python_script("experiments/001-representation-boundary/run_experiment.py"))
    command("provenance 001", python_script("research/tools/validate_provenance.py", provenance[0]), "PROVENANCE_VALID")
    command("experiment 002", python_script("experiments/002-continuation-boundary/run_experiment.py"))
    command("kill test 002", python_script("experiments/002-continuation-boundary/run_kill_test.py"), "cost-shape-adversary")
    command("provenance 002", python_script("research/tools/validate_provenance.py", provenance[1]), "PROVENANCE_VALID")

    codeine = subprocess.run(
        python_script("experiments/007-codeine-general-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if codeine.returncode != 0:
        raise RuntimeError("experiment 007 failed")
    codeine_result = json.loads(codeine.stdout)
    if (codeine_result["scenario_count"], codeine_result["matches"], codeine_result["mismatches"]) != (6, 5, 1):
        raise RuntimeError("experiment 007 expected 5/6 matches and one policy mismatch")
    print("PASS experiment 007")
    command("provenance 007", python_script("research/tools/validate_provenance.py", provenance[6]), "PROVENANCE_VALID")

    xanax = subprocess.run(
        python_script("experiments/008-xanax-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if xanax.returncode != 0:
        raise RuntimeError("experiment 008 failed")
    xanax_result = json.loads(xanax.stdout)
    if xanax_result["kill_tests"]["temporal_without_events"] != "unavailable":
        raise RuntimeError("experiment 008 temporal kill test failed")
    if not xanax_result["kill_tests"]["contract_signatures_distinguish_same_answers"]:
        raise RuntimeError("experiment 008 lost contract distinction")
    print("PASS experiment 008")
    command("provenance 008", python_script("research/tools/validate_provenance.py", provenance[7]), "PROVENANCE_VALID")

    command("generate VIZZ conditions", python_script("experiments/003-vizz-decision/generate_conditions.py"))
    command("verify VIZZ conditions", python_script("experiments/003-vizz-decision/verify_conditions.py"), "CONDITIONS_VALID")
    command("generate VIZZ pilot", python_script("experiments/003-vizz-decision/generate_pilot.py"))
    command("verify VIZZ pilot", python_script("experiments/003-vizz-decision/verify_pilot.py"), "PILOT_VALID")
    command("audit VIZZ pilot design", python_script("experiments/003-vizz-decision/audit_pilot_design.py"), "CARRYOVER_RISK=high")
    command("analyze VIZZ without human data", python_script("experiments/003-vizz-decision/analyze_pilot.py"), "NO_HUMAN_DATA")
    command("provenance 003", python_script("research/tools/validate_provenance.py", provenance[2]), "PROVENANCE_VALID")

    command("generate balanced VIZZ pilot", python_script("experiments/009-vizz-counterbalanced/generate_pilot.py"))
    command("verify balanced VIZZ pilot", python_script("experiments/009-vizz-counterbalanced/verify_pilot.py"), "BALANCED_PILOT_VALID")
    command("analyze balanced VIZZ without human data", python_script("experiments/009-vizz-counterbalanced/analyze_pilot.py"), "NO_HUMAN_DATA")
    command("aggregate balanced VIZZ without human data", python_script("experiments/009-vizz-counterbalanced/aggregate_pilot.py"), "NO_HUMAN_DATA")
    command("provenance 009", python_script("research/tools/validate_provenance.py", provenance[8]), "PROVENANCE_VALID")

    command("generate metamorphic cases", python_script("experiments/010-metamorphic-boundary/generate_cases.py"))
    metamorphic = subprocess.run(
        python_script("experiments/010-metamorphic-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if metamorphic.returncode != 0:
        raise RuntimeError("experiment 010 failed")
    metamorphic_result = json.loads(metamorphic.stdout)
    if metamorphic_result["case_count"] != 40 or not metamorphic_result["all_properties_hold"]:
        raise RuntimeError("experiment 010 metamorphic property failure")
    print("PASS experiment 010")
    command("provenance 010", python_script("research/tools/validate_provenance.py", provenance[9]), "PROVENANCE_VALID")

    command("generate polygon cases", python_script("experiments/011-nonrectangular-boundary/generate_cases.py"))
    polygon = subprocess.run(
        python_script("experiments/011-nonrectangular-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if polygon.returncode != 0:
        raise RuntimeError("experiment 011 failed")
    polygon_result = json.loads(polygon.stdout)
    if (polygon_result["case_count"], polygon_result["vertex_exact_matches"], polygon_result["bbox_false_positive_cases"]) != (20, 20, 20):
        raise RuntimeError("experiment 011 polygon loss property failure")
    print("PASS experiment 011")
    command("provenance 011", python_script("research/tools/validate_provenance.py", provenance[10]), "PROVENANCE_VALID")

    command("generate curve-layer cases", python_script("experiments/012-curves-layers-boundary/generate_cases.py"))
    curves = subprocess.run(
        python_script("experiments/012-curves-layers-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if curves.returncode != 0:
        raise RuntimeError("experiment 012 failed")
    curves_result = json.loads(curves.stdout)
    if (curves_result["case_count"], curves_result["table_visible_matches"], curves_result["bbox_hole_false_positive_cases"]) != (20, 20, 20):
        raise RuntimeError("experiment 012 curve/layer property failure")
    print("PASS experiment 012")
    command("provenance 012", python_script("research/tools/validate_provenance.py", provenance[11]), "PROVENANCE_VALID")

    vizz = subprocess.run(
        python_script("experiments/013-vizz-perceptual-adaptation/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if vizz.returncode != 0:
        raise RuntimeError("experiment 013 failed")
    vizz_result = json.loads(vizz.stdout)
    modes = {item["representation"] for item in vizz_result["representations"]}
    if vizz_result["event_count"] != 10 or modes != {"text", "timeline", "focus", "field"} or vizz_result["human_data"]:
        raise RuntimeError("experiment 013 VIZZ contract failure")
    print("PASS experiment 013")
    command("verify VIZZ 013", python_script("experiments/013-vizz-perceptual-adaptation/verify_vizz.py"), "VIZZ_PROTOTYPE_VALID")
    command("provenance 013", python_script("research/tools/validate_provenance.py", provenance[12]), "PROVENANCE_VALID")

    vizz_decision = subprocess.run(
        python_script("experiments/014-vizz-decision-query/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if vizz_decision.returncode != 0:
        raise RuntimeError("experiment 014 failed")
    vizz_decision_result = json.loads(vizz_decision.stdout)
    if (
        vizz_decision_result["event_count"],
        vizz_decision_result["oracle"]["anchor_event"],
        vizz_decision_result["oracle"]["tail_event_ids"],
    ) != (10, "e06", ["e07", "e08", "e09", "e10"]):
        raise RuntimeError("experiment 014 oracle mismatch")
    if not vizz_decision_result["representations"][0]["global_tail_available"]:
        raise RuntimeError("experiment 014 complete text lost global query")
    if vizz_decision_result["representations"][3]["global_tail_available"]:
        raise RuntimeError("experiment 014 aggregate recovered global query")
    print("PASS experiment 014")
    command(
        "kill test VIZZ decision 014",
        python_script("experiments/014-vizz-decision-query/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 014", python_script("research/tools/validate_provenance.py", provenance[13]), "PROVENANCE_VALID")

    vizz_session = subprocess.run(
        python_script("experiments/015-vizz-session-contract/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if vizz_session.returncode != 0:
        raise RuntimeError("experiment 015 failed")
    vizz_session_result = json.loads(vizz_session.stdout)
    if (
        vizz_session_result["accepted_cases"],
        vizz_session_result["human_data"],
        vizz_session_result["devices_started"],
        vizz_session_result["network_used"],
        vizz_session_result["raw_capture"],
    ) != (2, False, False, False, False):
        raise RuntimeError("experiment 015 session boundary failure")
    print("PASS experiment 015")
    command(
        "kill test VIZZ session 015",
        python_script("experiments/015-vizz-session-contract/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 015", python_script("research/tools/validate_provenance.py", provenance[14]), "PROVENANCE_VALID")

    codeine_state = subprocess.run(
        python_script("experiments/016-codeine-session-state/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if codeine_state.returncode != 0:
        raise RuntimeError("experiment 016 failed")
    codeine_state_result = json.loads(codeine_state.stdout)
    transition = codeine_state_result["transition"]
    if (
        codeine_state_result["event_count"],
        transition["last_significant_improvement"],
        transition["repetition_entry"],
        transition["drift"],
        codeine_state_result["human_data"],
        codeine_state_result["pharmacological_inference"],
    ) != (8, "c04", "c07", "unavailable_without_objective_signal", False, False):
        raise RuntimeError("experiment 016 CODE-INE transition boundary failure")
    print("PASS experiment 016")
    command(
        "kill test CODE-INE state 016",
        python_script("experiments/016-codeine-session-state/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 016", python_script("research/tools/validate_provenance.py", provenance[15]), "PROVENANCE_VALID")

    xanax_chain = subprocess.run(
        python_script("experiments/017-xanax-analogy-chain/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if xanax_chain.returncode != 0:
        raise RuntimeError("experiment 017 failed")
    xanax_chain_result = json.loads(xanax_chain.stdout)
    if (
        xanax_chain_result["search"]["selected_source"],
        xanax_chain_result["verification"]["prediction_verified"],
        xanax_chain_result["rupture"]["status"],
        xanax_chain_result["human_data"],
        xanax_chain_result["arbitrary_corpus"],
        xanax_chain_result["search"]["network_used"],
    ) != ("queue-interval", True, "break", False, False, False):
        raise RuntimeError("experiment 017 X-ANA-X chain boundary failure")
    print("PASS experiment 017")
    command(
        "kill test X-ANA-X chain 017",
        python_script("experiments/017-xanax-analogy-chain/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 017", python_script("research/tools/validate_provenance.py", provenance[16]), "PROVENANCE_VALID")

    command("experiment 004", python_script("experiments/004-ketamine-investment/run_experiment.py"))
    command("provenance 004", python_script("research/tools/validate_provenance.py", provenance[3]), "PROVENANCE_VALID")
    composition = subprocess.run(
        python_script("experiments/005-composition-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if composition.returncode != 0:
        raise RuntimeError("experiment 005 failed")
    composition_result = json.loads(composition.stdout)
    if composition_result["commutativity"]["graph_pair"] != "does_not_commute":
        raise RuntimeError("experiment 005 lost graph non-commutativity result")
    print("PASS experiment 005")
    command("provenance 005", python_script("research/tools/validate_provenance.py", provenance[4]), "PROVENANCE_VALID")

    ladder = subprocess.run(
        python_script("experiments/006-invariant-ladder/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if ladder.returncode != 0:
        raise RuntimeError("experiment 006 failed")
    ladder_result = json.loads(ladder.stdout)
    names = {item["representation"] for item in ladder_result["representations"]}
    expected_names = {"source", "geometry-table", "attribute-table", "indexed-table", "relation-graph", "attributed-graph", "temporal-state"}
    if names != expected_names:
        raise RuntimeError(f"experiment 006 representation set mismatch: {sorted(names)}")
    print("PASS experiment 006")
    command("provenance 006", python_script("research/tools/validate_provenance.py", provenance[5]), "PROVENANCE_VALID")
    print("SUITE_VALID")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"SUITE_INVALID: {exc}")
