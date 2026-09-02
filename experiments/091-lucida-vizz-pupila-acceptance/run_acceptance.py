"""Run an offline acceptance check from FARMAXIA 090 into LUCIDA engine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SOURCE_ROOT = HERE.parent / "090-farmaxia-adaptive-representation-layer"
sys.path.insert(0, str(SOURCE_ROOT))

from pupila_adapter import PupilaAdapter  # noqa: E402
from vizz_adapter import VizzAdapter  # noqa: E402


def _context(participant: str) -> dict[str, object]:
    return {
        "sessionId": "session-091",
        "roomId": "room-091",
        "surfaceId": "surface-091",
        "host": "offline-fixture",
        "task": "lucida-domain-acceptance",
        "capabilities": ["focus"],
        "viewport": {"width": 1920, "height": 1080, "unit": "px"},
        "participantRef": participant,
    }


def _focus_signal(participant: str, at_ms: int, focused: bool) -> dict[str, object]:
    return {
        "sessionId": "session-091",
        "roomId": "room-091",
        "surfaceId": "surface-091",
        "participantRef": participant,
        "kind": "focus",
        "atMs": at_ms,
        "value": {"focused": focused},
        "consent": True,
    }


def _engine_event_from_vizz(state: dict[str, object]) -> dict[str, object]:
    return {
        "session_id": str(state["sessionId"]),
        "event_id": "vizz-091-user-a",
        "timestamp": "2026-09-02T12:00:00Z",
        "sequence": 1,
        "event_type": "focus.state",
        "summary": {"focused": bool(state["focusState"])},
    }


def _engine_event_from_pupila(room: dict[str, object]) -> dict[str, object]:
    proposals = room.get("proposals")
    if not isinstance(proposals, list) or len(proposals) != 1:
        raise AssertionError("experiment 090 did not produce one coordination proposal")
    proposal = proposals[0]
    if not isinstance(proposal, dict):
        raise AssertionError("experiment 090 proposal is not an object")
    reason = str(proposal["reason"])
    return {
        "session_id": str(room["sessionId"]),
        "event_id": "pupila-091-room",
        "timestamp": "2026-09-02T12:00:01Z",
        "sequence": 1,
        "event_type": "coordination.proposal",
        "summary": {
            "participant_count": int(room["participantCount"]),
            "proposal_kind": str(proposal["kind"]),
            "proposal_state": str(proposal["state"]),
        },
        "proposal": {
            "proposal_id": str(proposal["proposalId"]),
            "kind": str(proposal["kind"]).replace("-", "_"),
            "title": "PUPILA coordination proposal",
            "body": reason,
            "priority": 60,
            "ttl_ms": 3000,
            "requires_confirmation": True,
            "reversible": True,
        },
    }


def _load_engine(lucida_root: Path):
    lucida_root = lucida_root.resolve()
    if not lucida_root.is_dir():
        raise FileNotFoundError(f"LUCIDA root does not exist: {lucida_root}")
    expected = lucida_root / "lucida" / "engine" / "domain_adapters.py"
    if not expected.is_file():
        raise FileNotFoundError(f"selected LUCIDA checkout lacks domain adapters: {expected}")
    for module_name in list(sys.modules):
        if module_name == "lucida" or module_name.startswith("lucida."):
            del sys.modules[module_name]
    sys.path.insert(0, str(lucida_root))
    import lucida  # noqa: PLC0415
    from lucida.engine import (  # noqa: PLC0415
        AdapterRegistry,
        ContractRegistry,
        LucidaPipeline,
        register_vizz_pupila_routes,
    )

    loaded_path = Path(lucida.__file__).resolve()
    try:
        loaded_path.relative_to(lucida_root)
    except ValueError as error:
        raise AssertionError(f"loaded LUCIDA package is outside selected root: {loaded_path}") from error
    return (
        AdapterRegistry,
        ContractRegistry,
        LucidaPipeline,
        register_vizz_pupila_routes,
        lucida_root,
        loaded_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lucida-root", required=True)
    args = parser.parse_args()
    (
        AdapterRegistry,
        ContractRegistry,
        LucidaPipeline,
        register_vizz_pupila_routes,
        lucida_root,
        loaded_path,
    ) = _load_engine(Path(args.lucida_root))

    vizz = VizzAdapter()
    pupila = PupilaAdapter()
    state_a = vizz.ingest(_context("user-a"), _focus_signal("user-a", 100, True))
    state_b = vizz.ingest(_context("user-b"), _focus_signal("user-b", 100, False))
    pupila.ingest(_context("user-a"), state_a)
    room = pupila.ingest(_context("user-b"), state_b)

    adapters = AdapterRegistry()
    contracts = ContractRegistry()
    register_vizz_pupila_routes(adapters, contracts)
    pipeline = LucidaPipeline(adapters, contracts)
    state = pipeline.initial_state("session-091")
    first = pipeline.apply(
        adapter_id="vizz.metadata",
        contract_id="vizz.perception.v1",
        value=_engine_event_from_vizz(state_a),
        state=state,
    )
    second = pipeline.apply(
        adapter_id="pupila.coordination",
        contract_id="pupila.coordination.v1",
        value=_engine_event_from_pupila(room),
        state=first.state,
    )
    report = {
        "lucidaRoot": str(lucida_root),
        "loadedLucidaPath": str(loaded_path),
        "sourceExperiment": "090-farmaxia-adaptive-representation-layer",
        "routes": ["vizz.metadata:vizz.perception.v1", "pupila.coordination:pupila.coordination.v1"],
        "stateRevision": second.state.revision,
        "activeProposalCount": len(second.state.active_proposals),
        "renderItemCount": len(second.plan.items),
        "renderSource": second.plan.items[0]["source"] if second.plan.items else None,
        "rawPayloadForwarded": False,
        "networkOpened": False,
        "guiOpened": False,
        "hostActionsExecuted": False,
    }
    assert report["stateRevision"] == 2
    assert report["activeProposalCount"] == 1
    assert report["renderItemCount"] == 1
    assert report["renderSource"] == "pupila"
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
