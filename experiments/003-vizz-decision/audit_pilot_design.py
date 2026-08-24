"""Audit whether the current VIZZ pilot confounds condition with carryover."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent
STATE = ROOT / "decision-state.json"
MANIFEST = ROOT / "conditions" / "manifest.json"
PILOT = ROOT / "pilot.html"


def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pilot = PILOT.read_text(encoding="utf-8")
    signatures = {manifest["data_signature"]}
    same_state = len(signatures) == 1 and next(iter(signatures)) in pilot and len(state["branches"]) > 0
    print("VIZZ_DESIGN_AUDIT")
    print(f"condition_signature_count={len(signatures)}")
    print(f"single_trial_state={same_state}")
    if same_state:
        print("CARRYOVER_RISK=high")
        print("RECOMMENDATION=counterbalance_distinct_trial_sets_before_causal_inference")
    else:
        print("CARRYOVER_RISK=not_established")


if __name__ == "__main__":
    main()
