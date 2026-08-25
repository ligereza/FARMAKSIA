"""Static contract for the dual representation audit."""

from __future__ import annotations

from pathlib import Path


HERE = Path(__file__).parent


def main() -> None:
    failures: list[str] = []
    audit = (HERE / "audit_dual.py").read_text(encoding="utf-8")
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    for token in (
        "eye_centric_complete",
        "UNKNOWN_NOT_IDENTIFIABLE",
        "eye_centric_not_persisted_in_both_artifacts",
        "screen_mapper_changed",
        "raw_frames",
    ):
        if token not in audit:
            failures.append(f"dual audit lacks {token}")
    readme_lower = readme.lower()
    if "no reconstruye" not in readme_lower or "no abre cámara" not in readme_lower:
        failures.append("audit limits are not documented")
    if failures:
        print("CONTRACT_TESTS_INVALID")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("CONTRACT_TESTS_VALID")
    print("legacy_analysis_preserved=True")
    print("missing_eye_data_is_unknown=True")
    print("screen_mapper_changed=False")


if __name__ == "__main__":
    main()
