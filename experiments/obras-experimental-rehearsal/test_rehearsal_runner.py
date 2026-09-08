from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from run_rehearsal import HERE, run


def test_runner_emits_predictive_transport_and_console_proposals(tmp_path):
    output = tmp_path / "evidence"
    summary = run(
        Namespace(
            output=str(output),
            fixture=str(HERE / "fixture-synthetic-audio.json"),
            xio_root=r"C:\IA\XIO",
            mosaik_root=r"C:\IA\VJ",
            session_id="runner-test-001",
            session_start="2026-01-01T20:00:00Z",
            fps=25,
            fixtures=5,
        )
    )

    assert summary["status"] == "PASS"
    assert summary["predictive_replay_status"] == "PASS"
    assert summary["console_proposal_status"] == "PASS"
    transport = json.loads((output / "predictive-transport.json").read_text(encoding="utf-8"))
    assert transport["all_packets_roundtrip"] is True
    assert transport["direct_dmx_universes"] == 1
    assert transport["semantic_packet_bytes"] < transport["direct_dmx_channel_bytes"]

    proposals = json.loads((output / "console-proposals.json").read_text(encoding="utf-8"))
    assert len(proposals["proposals"]) == 7
    assert all(item["status"] == "PENDING_APPROVAL" for item in proposals["proposals"])
    assert proposals["revocation"]["status"] == "BLOCKED"
    assert all(
        item["safety"]["external_side_effects"] is False
        for item in proposals["proposals"]
    )

    safety = json.loads((output / "safety-summary.json").read_text(encoding="utf-8"))
    assert all(safety["scenarios"].values())
    assert safety["external_side_effects"] is False
    assert (output / "predictive-frames.jsonl").is_file()
    assert (output / "semantic-replay.json").is_file()
