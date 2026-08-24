"""Kill tests for the X-ANA-X versus reformulation comparison."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("xanax_control_runner", HERE / "run_experiment.py")
if SPEC is None or SPEC.loader is None:
    raise SystemExit("KILL_TEST_INVALID: could not load runner")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def main() -> None:
    text = RUNNER.TARGET.read_text(encoding="utf-8")
    facts = RUNNER.analyze_source(text)
    if not facts["wrapper_failure_guard"] or not facts["terminal_marker_present"]:
        raise SystemExit("KILL_TEST_INVALID: valid target lost its guard or marker")
    adversarial_guard = RUNNER.analyze_source(text.replace("completed.returncode != 0", "completed.returncode == 0", 1))
    if adversarial_guard["wrapper_failure_guard"]:
        raise SystemExit("KILL_TEST_INVALID: inverted comparator still passed guard test")
    adversarial_marker = RUNNER.analyze_source(text.replace('print("SUITE_VALID")', 'print("SUITE_NOT_VALID")', 1))
    if adversarial_marker["terminal_marker_present"]:
        raise SystemExit("KILL_TEST_INVALID: removed terminal marker still detected")
    source = json.loads(RUNNER.SOURCE_CARD.read_text(encoding="utf-8"))
    direct = RUNNER.direct_route(facts)
    analogy = RUNNER.analogy_route(facts, source)
    if direct["decision"] != analogy["predicted_decision"]:
        raise SystemExit("KILL_TEST_INVALID: routes unexpectedly diverged")
    if direct["decision"] == "terminal_requires_failure_guard" and not facts["guards_before_terminal"]:
        raise SystemExit("KILL_TEST_INVALID: terminal order claim was unsupported")
    print("KILL_TESTS_VALID")
    print("analogy_unique_decision=not_demonstrated")
    print("inverted_guard=unavailable")


if __name__ == "__main__":
    main()
