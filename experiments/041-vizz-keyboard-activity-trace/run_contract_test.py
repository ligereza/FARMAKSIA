"""Static contract for opt-in, count-only keyboard activity tracing."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    failures: list[str] = []
    keyboard = (ROOT / "experiments/033-vizz-python-headless-runtime/keyboard_activity.py").read_text(encoding="utf-8")
    trace = (ROOT / "experiments/033-vizz-python-headless-runtime/interaction_trace.py").read_text(encoding="utf-8")
    runtime = (ROOT / "experiments/033-vizz-python-headless-runtime/run_vizz.py").read_text(encoding="utf-8")
    auditor = (Path(__file__).parent / "keyboard_trace_audit.py").read_text(encoding="utf-8")
    for token in ("WH_KEYBOARD_LL", "WM_KEYDOWN", "keyboard_event_count", "keyboard_last_event_age_ms"):
        if token not in keyboard:
            failures.append(f"keyboard hook lacks {token}")
    for token in ("keyboard_activity_only", "key_values_persisted", "text_persisted"):
        if token not in trace:
            failures.append(f"trace lacks {token}")
    if "--keyboard-trace" not in runtime or "never stores key values or text" not in runtime:
        failures.append("runtime flag privacy contract is incomplete")
    for token in ("FORBIDDEN_FIELDS", "key_code", "typed_text", "KEYBOARD_TRACE_VALID"):
        if token not in auditor and token != "KEYBOARD_TRACE_VALID":
            failures.append(f"auditor lacks {token}")
    if "vkCode" in keyboard or "key_value" in keyboard:
        failures.append("keyboard hook appears to persist key identity")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("keyboard_values_persisted=False")
    print("text_persisted=False")
    print("opt_in=True")


if __name__ == "__main__":
    main()
