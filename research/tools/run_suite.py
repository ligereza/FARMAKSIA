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
        "experiments/018-xanax-reformulation-control/provenance.json",
        "experiments/019-xanax-provenance-archive-audit/provenance.json",
        "experiments/020-vizz-codeine-event-bridge/provenance.json",
        "experiments/021-manual-adapter-gate/provenance.json",
        "experiments/022-vizz-codeine-long-bridge/provenance.json",
        "experiments/023-vizz-codeine-observability-boundary/provenance.json",
        "experiments/024-vizz-latency-coverage-boundary/provenance.json",
        "experiments/025-vizz-display-condition-invariance/provenance.json",
        "experiments/026-codeine-objective-signal/provenance.json",
        "experiments/027-codeine-objective-oracle/provenance.json",
        "experiments/028-vizz-gaze-quality-gate/provenance.json",
        "experiments/029-codeine-executable-oracle/provenance.json",
        "experiments/030-vizz-webgazer-opt-in/provenance.json",
        "experiments/031-vizz-gpu-only-deep-tracker/provenance.json",
        "experiments/032-vizz-python-flow-split/provenance.json",
        "experiments/033-vizz-python-headless-runtime/provenance.json",
        "experiments/034-vizz-pretrained-model-probe/provenance.json",
        "experiments/035-vizz-eye-centric-normalization/provenance.json",
        "experiments/036-vizz-eye-centric-capture-contract/provenance.json",
        "experiments/037-vizz-dual-representation-audit/provenance.json",
        "experiments/038-vizz-naturalistic-trace/provenance.json",
        "experiments/039-vizz-github-pretrained-gaze/provenance.json",
        "experiments/040-vizz-naturalistic-trace-audit/provenance.json",
        "experiments/041-vizz-keyboard-activity-trace/provenance.json",
        "experiments/044-vizz-reduced-eye-camera/provenance.json",
        "experiments/045-vizz-single-eye-camera/provenance.json",
        "experiments/046-vizz-gaze-geometry-probe/provenance.json",
        "experiments/047-vizz-controlled-playback/provenance.json",
        "experiments/048-vizz-passive-observer/provenance.json",
        "experiments/049-vizz-runtime-geometry-bridge/provenance.json",
    ]

    command("compile Python", [PYTHON, "-m", "compileall", "-q", "research", "experiments"])
    command("validate empty corpus manifest", python_script("research/tools/validate_corpus_manifest.py"), "CORPUS_VALID")
    command("audit consolidated lab state", python_script("research/tools/audit_lab_state.py"), "LAB_STATE_VALID")
    command("audit laboratory completion", python_script("research/tools/audit_lab_completion.py"), "LAB_COMPLETION_VALID")
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

    xanax_control = subprocess.run(
        python_script("experiments/018-xanax-reformulation-control/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if xanax_control.returncode != 0:
        raise RuntimeError("experiment 018 failed")
    xanax_control_result = json.loads(xanax_control.stdout)
    comparison = xanax_control_result["comparison"]
    if (
        comparison["same_facts"],
        comparison["same_decision"],
        comparison["unique_analogy_decision"],
        comparison["novelty_status"],
        xanax_control_result["human_data"],
        xanax_control_result["network_used"],
        xanax_control_result["arbitrary_corpus"],
    ) != (True, True, False, "not_demonstrated", False, False, False):
        raise RuntimeError("experiment 018 X-ANA-X reformulation control failure")
    print("PASS experiment 018")
    command(
        "kill test X-ANA-X control 018",
        python_script("experiments/018-xanax-reformulation-control/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 018", python_script("research/tools/validate_provenance.py", provenance[17]), "PROVENANCE_VALID")

    xanax_archive = subprocess.run(
        python_script("experiments/019-xanax-provenance-archive-audit/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if xanax_archive.returncode != 0:
        raise RuntimeError("experiment 019 failed")
    xanax_archive_result = json.loads(xanax_archive.stdout)
    if (
        xanax_archive_result["comparison"]["same_statuses"],
        xanax_archive_result["comparison"]["unique_analogy_decision"],
        xanax_archive_result["comparison"]["novelty_status"],
        xanax_archive_result["human_data"],
        xanax_archive_result["network_used"],
        xanax_archive_result["arbitrary_corpus"],
    ) != (True, False, "not_demonstrated", False, False, False):
        raise RuntimeError("experiment 019 X-ANA-X archive audit failure")
    print("PASS experiment 019")
    command(
        "kill test X-ANA-X archive 019",
        python_script("experiments/019-xanax-provenance-archive-audit/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 019", python_script("research/tools/validate_provenance.py", provenance[18]), "PROVENANCE_VALID")

    bridge = subprocess.run(
        python_script("experiments/020-vizz-codeine-event-bridge/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if bridge.returncode != 0:
        raise RuntimeError("experiment 020 failed")
    bridge_result = json.loads(bridge.stdout)
    if (
        bridge_result["vizz_event_count"],
        bridge_result["codeine_event_count"],
        bridge_result["transition"]["last_significant_improvement"],
        bridge_result["transition"]["repetition_entry"],
        bridge_result["human_data"],
        bridge_result["devices_started"],
        bridge_result["network_used"],
        bridge_result["raw_capture"],
    ) != (3, 3, "s02", None, False, False, False, False):
        raise RuntimeError("experiment 020 VIZZ-CODE-INE bridge boundary failure")
    print("PASS experiment 020")
    command(
        "kill test VIZZ-CODE-INE bridge 020",
        python_script("experiments/020-vizz-codeine-event-bridge/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 020", python_script("research/tools/validate_provenance.py", provenance[19]), "PROVENANCE_VALID")

    manual_adapter = subprocess.run(
        python_script("experiments/021-manual-adapter-gate/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if manual_adapter.returncode != 0:
        raise RuntimeError("experiment 021 failed")
    manual_adapter_result = json.loads(manual_adapter.stdout)
    if (
        manual_adapter_result["consent_gate"],
        manual_adapter_result["validated_event_count"],
        manual_adapter_result["dry_run_valid"],
        manual_adapter_result["session_written"],
        manual_adapter_result["human_data"],
        manual_adapter_result["devices_started"],
        manual_adapter_result["network_used"],
        manual_adapter_result["raw_capture"],
    ) != (True, 3, True, False, False, False, False, False):
        raise RuntimeError("experiment 021 manual adapter gate failure")
    print("PASS experiment 021")
    command(
        "kill test manual adapter 021",
        python_script("experiments/021-manual-adapter-gate/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 021", python_script("research/tools/validate_provenance.py", provenance[20]), "PROVENANCE_VALID")

    long_bridge = subprocess.run(
        python_script("experiments/022-vizz-codeine-long-bridge/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if long_bridge.returncode != 0:
        raise RuntimeError("experiment 022 failed")
    long_bridge_result = json.loads(long_bridge.stdout)
    transition = long_bridge_result["transition"]
    if (
        long_bridge_result["vizz_event_count"],
        long_bridge_result["codeine_event_count"],
        transition["last_significant_improvement"],
        transition["repetition_entry"],
        long_bridge_result["dry_run_valid"],
        long_bridge_result["session_written"],
        long_bridge_result["human_data"],
        long_bridge_result["pharmacological_inference"],
        long_bridge_result["raw_capture"],
    ) != (8, 8, "c04", "c07", True, False, False, False, False):
        raise RuntimeError("experiment 022 long VIZZ-CODE-INE bridge failure")
    print("PASS experiment 022")
    command(
        "kill test long VIZZ-CODE-INE bridge 022",
        python_script("experiments/022-vizz-codeine-long-bridge/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 022", python_script("research/tools/validate_provenance.py", provenance[21]), "PROVENANCE_VALID")

    observability = subprocess.run(
        python_script("experiments/023-vizz-codeine-observability-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if observability.returncode != 0:
        raise RuntimeError("experiment 023 failed")
    observability_result = json.loads(observability.stdout)
    if (
        observability_result["case_count"],
        observability_result["classification_counts"],
        observability_result["all_expected_classifications"],
        observability_result["baseline_transition"]["last_significant_improvement"],
        observability_result["baseline_transition"]["repetition_entry"],
        observability_result["human_data"],
        observability_result["devices_started"],
        observability_result["network_used"],
        observability_result["raw_capture"],
        observability_result["pharmacological_inference"],
    ) != (7, {"available": 1, "rejected": 3, "ambiguous": 3}, True, "c04", "c07", False, False, False, False, False):
        raise RuntimeError("experiment 023 observability boundary failure")
    print("PASS experiment 023")
    command(
        "kill test VIZZ-CODE-INE observability 023",
        python_script("experiments/023-vizz-codeine-observability-boundary/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 023", python_script("research/tools/validate_provenance.py", provenance[22]), "PROVENANCE_VALID")

    latency = subprocess.run(
        python_script("experiments/024-vizz-latency-coverage-boundary/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if latency.returncode != 0:
        raise RuntimeError("experiment 024 failed")
    latency_result = json.loads(latency.stdout)
    if (
        latency_result["case_count"],
        latency_result["classification_counts"],
        latency_result["all_expected_classifications"],
        latency_result["baseline_transition"]["last_significant_improvement"],
        latency_result["baseline_transition"]["repetition_entry"],
        latency_result["human_data"],
        latency_result["devices_started"],
        latency_result["network_used"],
        latency_result["raw_capture"],
        latency_result["pharmacological_inference"],
    ) != (5, {"available": 2, "unavailable": 3}, True, "c04", "c07", False, False, False, False, False):
        raise RuntimeError("experiment 024 latency coverage boundary failure")
    print("PASS experiment 024")
    command(
        "kill test VIZZ latency coverage 024",
        python_script("experiments/024-vizz-latency-coverage-boundary/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 024", python_script("research/tools/validate_provenance.py", provenance[23]), "PROVENANCE_VALID")

    display = subprocess.run(
        python_script("experiments/025-vizz-display-condition-invariance/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if display.returncode != 0:
        raise RuntimeError("experiment 025 failed")
    display_result = json.loads(display.stdout)
    if (
        display_result["case_count"],
        display_result["classification_counts"],
        display_result["all_expected_classifications"],
        display_result["full_display_invariant"],
        display_result["baseline_transition"]["last_significant_improvement"],
        display_result["baseline_transition"]["repetition_entry"],
        display_result["human_data"],
        display_result["devices_started"],
        display_result["network_used"],
        display_result["raw_capture"],
        display_result["physiological_inference"],
        display_result["pharmacological_inference"],
        display_result["optical_prescription_applied"],
    ) != (6, {"available": 4, "unavailable": 2}, True, True, "c04", "c07", False, False, False, False, False, False, False):
        raise RuntimeError("experiment 025 display condition invariance failure")
    print("PASS experiment 025")
    command(
        "kill test VIZZ display condition 025",
        python_script("experiments/025-vizz-display-condition-invariance/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 025", python_script("research/tools/validate_provenance.py", provenance[24]), "PROVENANCE_VALID")

    objective_signal = subprocess.run(
        python_script("experiments/026-codeine-objective-signal/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if objective_signal.returncode != 0:
        raise RuntimeError("experiment 026 failed")
    objective_result = json.loads(objective_signal.stdout)
    if (
        objective_result["case_count"],
        objective_result["classification_counts"],
        objective_result["all_expected_classifications"],
        objective_result["baseline_transition"]["last_significant_improvement"],
        objective_result["baseline_transition"]["repetition_entry"],
        objective_result["human_data"],
        objective_result["devices_started"],
        objective_result["network_used"],
        objective_result["raw_capture"],
        objective_result["pharmacological_inference"],
        objective_result["neurochemical_inference"],
    ) != (6, {"available": 3, "unavailable": 2, "rejected": 1}, True, "c04", "c07", False, False, False, False, False, False):
        raise RuntimeError("experiment 026 objective signal boundary failure")
    print("PASS experiment 026")
    command(
        "kill test CODE-INE objective signal 026",
        python_script("experiments/026-codeine-objective-signal/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 026", python_script("research/tools/validate_provenance.py", provenance[25]), "PROVENANCE_VALID")

    objective_oracle = subprocess.run(
        python_script("experiments/027-codeine-objective-oracle/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if objective_oracle.returncode != 0:
        raise RuntimeError("experiment 027 failed")
    oracle_result = json.loads(objective_oracle.stdout)
    if (
        oracle_result["case_count"],
        oracle_result["evidence_status_counts"],
        oracle_result["all_expected_classifications"],
        oracle_result["baseline_transition"]["last_significant_improvement"],
        oracle_result["baseline_transition"]["repetition_entry"],
        oracle_result["human_data"],
        oracle_result["devices_started"],
        oracle_result["network_used"],
        oracle_result["raw_capture"],
        oracle_result["pharmacological_inference"],
        oracle_result["neurochemical_inference"],
    ) != (7, {"verified": 3, "declared_only": 1, "conflict": 1, "unavailable": 1, "rejected": 1}, True, "c04", "c07", False, False, False, False, False, False):
        raise RuntimeError("experiment 027 CODE-INE objective oracle boundary failure")
    print("PASS experiment 027")
    command(
        "kill test CODE-INE objective oracle 027",
        python_script("experiments/027-codeine-objective-oracle/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 027", python_script("research/tools/validate_provenance.py", provenance[26]), "PROVENANCE_VALID")

    gaze_quality = subprocess.run(
        python_script("experiments/028-vizz-gaze-quality-gate/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if gaze_quality.returncode != 0:
        raise RuntimeError("experiment 028 failed")
    gaze_result = json.loads(gaze_quality.stdout)
    if (
        gaze_result["case_count"],
        gaze_result["evidence_status_counts"],
        gaze_result["all_expected_classifications"],
        gaze_result["baseline_transition"]["last_significant_improvement"],
        gaze_result["baseline_transition"]["repetition_entry"],
        gaze_result["human_data"],
        gaze_result["devices_started"],
        gaze_result["network_used"],
        gaze_result["raw_capture"],
        gaze_result["physiological_inference"],
        gaze_result["pharmacological_inference"],
        gaze_result["neurochemical_inference"],
    ) != (11, {"available": 1, "blocked": 3, "unavailable": 5, "rejected": 2}, True, "c04", "c07", False, False, False, False, False, False, False):
        raise RuntimeError("experiment 028 VIZZ gaze quality boundary failure")
    print("PASS experiment 028")
    command(
        "kill test VIZZ gaze quality 028",
        python_script("experiments/028-vizz-gaze-quality-gate/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 028", python_script("research/tools/validate_provenance.py", provenance[27]), "PROVENANCE_VALID")

    executable_oracle = subprocess.run(
        python_script("experiments/029-codeine-executable-oracle/run_experiment.py"),
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if executable_oracle.returncode != 0:
        raise RuntimeError("experiment 029 failed")
    executable_result = json.loads(executable_oracle.stdout)
    if (
        executable_result["case_count"],
        executable_result["evidence_status_counts"],
        executable_result["all_expected_classifications"],
        executable_result["baseline_transition"]["last_significant_improvement"],
        executable_result["baseline_transition"]["repetition_entry"],
        executable_result["oracle_reads_objective_scores"],
        executable_result["human_data"],
        executable_result["devices_started"],
        executable_result["network_used"],
        executable_result["raw_capture"],
        executable_result["pharmacological_inference"],
        executable_result["neurochemical_inference"],
    ) != (9, {"verified": 3, "conflict": 2, "unavailable": 1, "rejected": 3}, True, "c04", "c07", False, False, False, False, False, False, False):
        raise RuntimeError("experiment 029 CODE-INE executable oracle boundary failure")
    print("PASS experiment 029")
    command(
        "kill test CODE-INE executable oracle 029",
        python_script("experiments/029-codeine-executable-oracle/run_kill_test.py"),
        "KILL_TESTS_VALID",
    )
    command("provenance 029", python_script("research/tools/validate_provenance.py", provenance[28]), "PROVENANCE_VALID")

    command(
        "contract test VIZZ WebGazer 030",
        python_script("experiments/030-vizz-webgazer-opt-in/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 030", python_script("research/tools/validate_provenance.py", provenance[29]), "PROVENANCE_VALID")
    command(
        "contract test VIZZ GPU-only 031",
        python_script("experiments/031-vizz-gpu-only-deep-tracker/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 031", python_script("research/tools/validate_provenance.py", provenance[30]), "PROVENANCE_VALID")
    command(
        "contract test VIZZ Python flow split 032",
        python_script("experiments/032-vizz-python-flow-split/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 032", python_script("research/tools/validate_provenance.py", provenance[31]), "PROVENANCE_VALID")
    command(
        "contract test VIZZ Python headless runtime 033",
        python_script("experiments/033-vizz-python-headless-runtime/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 033", python_script("research/tools/validate_provenance.py", provenance[32]), "PROVENANCE_VALID")
    command(
        "contract test VIZZ pretrained model probe 034",
        python_script("experiments/034-vizz-pretrained-model-probe/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 034", python_script("research/tools/validate_provenance.py", provenance[33]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ eye-centric normalization 035",
        python_script("experiments/035-vizz-eye-centric-normalization/run_experiment.py"),
        "EYE_CENTRIC_VALID",
    )
    command(
        "contract test VIZZ eye-centric normalization 035",
        python_script("experiments/035-vizz-eye-centric-normalization/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 035", python_script("research/tools/validate_provenance.py", provenance[34]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ eye-centric capture contract 036",
        python_script("experiments/036-vizz-eye-centric-capture-contract/run_experiment.py"),
        "EYE_CENTRIC_CAPTURE_VALID",
    )
    command(
        "contract test VIZZ eye-centric capture 036",
        python_script("experiments/036-vizz-eye-centric-capture-contract/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 036", python_script("research/tools/validate_provenance.py", provenance[35]), "PROVENANCE_VALID")
    command(
        "contract test VIZZ dual representation audit 037",
        python_script("experiments/037-vizz-dual-representation-audit/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 037", python_script("research/tools/validate_provenance.py", provenance[36]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ naturalistic trace 038",
        python_script("experiments/038-vizz-naturalistic-trace/run_experiment.py"),
        "NATURALISTIC_TRACE_VALID",
    )
    command(
        "contract test VIZZ naturalistic trace 038",
        python_script("experiments/038-vizz-naturalistic-trace/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 038", python_script("research/tools/validate_provenance.py", provenance[37]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ GitHub pretrained gaze 039",
        python_script("experiments/039-vizz-github-pretrained-gaze/run_experiment.py"),
        "GITHUB_PRETRAINED_GAZE_VALID",
    )
    command(
        "contract test VIZZ GitHub pretrained gaze 039",
        python_script("experiments/039-vizz-github-pretrained-gaze/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 039", python_script("research/tools/validate_provenance.py", provenance[38]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ naturalistic trace audit 040",
        python_script("experiments/040-vizz-naturalistic-trace-audit/run_experiment.py"),
        "TRACE_AUDIT_VALID",
    )
    command(
        "contract test VIZZ naturalistic trace audit 040",
        python_script("experiments/040-vizz-naturalistic-trace-audit/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 040", python_script("research/tools/validate_provenance.py", provenance[39]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ keyboard activity trace 041",
        python_script("experiments/041-vizz-keyboard-activity-trace/run_experiment.py"),
        "KEYBOARD_TRACE_VALID",
    )
    command(
        "contract test VIZZ keyboard activity trace 041",
        python_script("experiments/041-vizz-keyboard-activity-trace/run_contract_test.py"),
        "CONTRACT_TESTS_VALID",
    )
    command("provenance 041", python_script("research/tools/validate_provenance.py", provenance[40]), "PROVENANCE_VALID")
    command(
        "contract test VIZZ reduced eye camera 044",
        python_script("experiments/044-vizz-reduced-eye-camera/run_contract_test.py"),
        "VIZZ_044_OPTICAL_CONTRACT_VALID",
    )
    command("provenance 044", python_script("research/tools/validate_provenance.py", provenance[41]), "PROVENANCE_VALID")
    command(
        "contract test VIZZ single eye camera 045",
        python_script("experiments/045-vizz-single-eye-camera/run_contract_test.py"),
        "VIZZ_045_RETIREMENT_CONTRACT_VALID",
    )
    command("provenance 045", python_script("research/tools/validate_provenance.py", provenance[42]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ gaze geometry 046",
        python_script("experiments/046-vizz-gaze-geometry-probe/run_experiment.py"),
        '"screen_content_mutated": false',
    )
    command(
        "contract test VIZZ gaze geometry 046",
        python_script("experiments/046-vizz-gaze-geometry-probe/run_contract_test.py"),
        "VIZZ_046_GEOMETRY_CONTRACT_VALID",
    )
    command("provenance 046", python_script("research/tools/validate_provenance.py", provenance[43]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ controlled playback 047",
        python_script("experiments/047-vizz-controlled-playback/run_experiment.py"),
        '"screen_content_mutated": false',
    )
    command(
        "contract test VIZZ controlled playback 047",
        python_script("experiments/047-vizz-controlled-playback/run_contract_test.py"),
        "VIZZ_047_PLAYBACK_CONTRACT_VALID",
    )
    command("provenance 047", python_script("research/tools/validate_provenance.py", provenance[44]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ passive observer 048",
        python_script("experiments/048-vizz-passive-observer/run_experiment.py"),
        '"screen_content_mutated": false',
    )
    command(
        "contract test VIZZ passive observer 048",
        python_script("experiments/048-vizz-passive-observer/run_contract_test.py"),
        "VIZZ_048_PASSIVE_TRACE_CONTRACT_VALID",
    )
    command("provenance 048", python_script("research/tools/validate_provenance.py", provenance[45]), "PROVENANCE_VALID")
    command(
        "experiment VIZZ runtime geometry bridge 049",
        python_script("experiments/049-vizz-runtime-geometry-bridge/run_experiment.py"),
        '"screen_content_mutated": false',
    )
    command(
        "contract test VIZZ runtime geometry bridge 049",
        python_script("experiments/049-vizz-runtime-geometry-bridge/run_contract_test.py"),
        "VIZZ_049_RUNTIME_BRIDGE_CONTRACT_VALID",
    )
    command("provenance 049", python_script("research/tools/validate_provenance.py", provenance[46]), "PROVENANCE_VALID")

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
