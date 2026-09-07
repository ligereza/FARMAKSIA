from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


class LucidaConsumerError(RuntimeError):
    pass


class LucidaConsumerSession:
    """Long-lived VJ consumer isolated from the engine Python process."""

    def __init__(self, lucida_root: str | Path):
        self.root = Path(lucida_root).resolve()
        if not self.root.is_dir():
            raise LucidaConsumerError(f"LUCIDA root does not exist: {self.root}")
        self.process = subprocess.Popen([sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(self.root)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        self._previous: Mapping[str, Any] | None = None
        self._sequence = 0

    def _request(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if self.process.poll() is not None or self.process.stdin is None or self.process.stdout is None:
            raise LucidaConsumerError("LUCIDA consumer worker is not running")
        try:
            self.process.stdin.write(json.dumps(payload, ensure_ascii=True) + "\n")
            self.process.stdin.flush()
            line = self.process.stdout.readline()
            result = json.loads(line)
        except (OSError, json.JSONDecodeError) as exc:
            raise LucidaConsumerError(f"LUCIDA worker communication failed: {exc}") from exc
        if not result.get("ok"):
            raise LucidaConsumerError(result.get("error", "LUCIDA worker rejected request"))
        return result

    def accept_snapshot(self, view: Mapping[str, Any], recovery: bool = False) -> dict[str, Any]:
        result = self._request({"op": "snapshot", "view": dict(view), "sequence": self._sequence, "recovery": recovery})
        self._previous = dict(view)
        return result

    def apply(self, view: Mapping[str, Any]) -> dict[str, Any]:
        if self._previous is None:
            raise LucidaConsumerError("initial snapshot is required")
        self._sequence += 1
        result = self._request({"op": "update", "previous": dict(self._previous), "view": dict(view), "sequence": self._sequence})
        self._previous = dict(view)
        return result

    def checkpoint(self) -> dict[str, Any]:
        return self._request({"op": "checkpoint"})["checkpoint"]

    def close(self):
        if self.process.stdin:
            try: self.process.stdin.close()
            except OSError: pass
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)

    def __enter__(self): return self
    def __exit__(self, *_args): self.close()


def consume_views(views: list[Mapping[str, Any]], lucida_root: str | Path) -> dict[str, Any]:
    if not views:
        raise LucidaConsumerError("at least one view is required")
    with LucidaConsumerSession(lucida_root) as session:
        session.accept_snapshot(views[0])
        applied = [session.apply(view) for view in views[1:]]
        checkpoint = session.checkpoint()
        return {"lucidaRoot": str(Path(lucida_root).resolve()), "appliedUpdateCount": checkpoint["applied_delta_count"], "finalProposalCount": len(views[-1]["pending_proposals"]), "applied": applied, "safety": views[-1]["safety"], "consumerCheckpoint": checkpoint}


def _worker(root: str):
    sys.path.insert(0, str(Path(root).resolve()))
    from lucida.overlay import diff_overlay_view, overlay_view_digest
    from lucida.overlay_consumer import OverlayConsumer
    consumer = OverlayConsumer()
    previous = None
    for line in sys.stdin:
        try:
            request = json.loads(line)
            op = request.get("op")
            if op == "snapshot":
                view = request["view"]; session_id = view["session_id"]
                cursor = _cursor(session_id, request["sequence"], None)
                consumer.accept_snapshot(view, cursor, recovery=bool(request.get("recovery", False))); previous = view
                output = {"ok": True, "checkpoint": consumer.checkpoint()}
            elif op == "update":
                view = request["view"]; session_id = view["session_id"]; changes = diff_overlay_view(request["previous"], view)
                update = {"contract_type": "LucidaOverlayUpdate", "schema_version": "0.1", "surface": "LUCIDA", "mode": "read_only", "view": view, "view_digest": overlay_view_digest(view), "changes": changes, "cursor": _cursor(session_id, request["sequence"], f"engine-state-{request['sequence']}"), "safety": {"proposal_only": True, "automatic_actions": False, "external_side_effects": False}}
                consumer.apply_update(update); previous = view
                output = {"ok": True, "checkpoint": consumer.checkpoint(), "changeCount": len(changes)}
            elif op == "checkpoint": output = {"ok": True, "checkpoint": consumer.checkpoint()}
            else: raise ValueError("unknown worker operation")
            sys.stdout.write(json.dumps(output, ensure_ascii=True) + "\n"); sys.stdout.flush()
        except Exception as exc:
            sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True) + "\n"); sys.stdout.flush()


def _cursor(session_id: str, sequence: int, event_id: str | None):
    return {"contract_type": "LucidaOverlayCursor", "schema_version": "0.1", "surface": "LUCIDA", "mode": "read_only", "session_id": session_id, "sequence": sequence, "last_event_id": event_id, "last_timestamp": None, "checkpoint_id": f"checkpoint-{sequence}", "safety": {"proposal_only": True, "automatic_actions": False, "external_side_effects": False}}


if __name__ == "__main__" and len(sys.argv) >= 3 and sys.argv[1] == "--worker":
    _worker(sys.argv[2])
