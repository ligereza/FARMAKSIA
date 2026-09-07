"""Durable temporal shell around the native FARMAKSIA 090 semantics."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from canonical_event_bridge import CanonicalEventBridge, CanonicalEventReplay
from pupila_lucida_projection import project_pupila_for_lucida
from lucida_render_plan import build_lucida_render_plan
from temporal_reference import eligible_events


class TemporalCoordinator:
    """Persist facts and clocks; derive PUPILA/LUCIDA views by replay."""

    def __init__(self, database: str | Path, *, stale_after_ms: int = 30_000) -> None:
        self.database = str(database)
        self.stale_after_ms = int(stale_after_ms)
        self._db = sqlite3.connect(self.database, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY, room_id TEXT NOT NULL, surface_id TEXT NOT NULL,
                context_json TEXT NOT NULL, logical_now INTEGER NOT NULL DEFAULT 0, revision INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS participants (
                session_id TEXT NOT NULL, peer_id TEXT NOT NULL, consent INTEGER NOT NULL,
                consent_epoch INTEGER NOT NULL DEFAULT 0, active_from INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (session_id, peer_id), FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, peer_id TEXT NOT NULL,
                source_ms INTEGER NOT NULL, consent_epoch INTEGER NOT NULL, accepted INTEGER NOT NULL,
                event_json TEXT NOT NULL, FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, proposal_id TEXT NOT NULL,
                request_id TEXT NOT NULL UNIQUE, proposal_version INTEGER NOT NULL, status TEXT NOT NULL,
                reverted_decision_id TEXT, FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );
            """
        )
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    def consent(self, session_id: str, peer_id: str, allowed: bool, *, active_from_ms: int = 0) -> int:
        with self._db:
            if self._db.execute("SELECT 1 FROM sessions WHERE session_id=?", (session_id,)).fetchone() is None:
                self._db.execute(
                    "INSERT INTO sessions(session_id,room_id,surface_id,context_json) VALUES (?,?,?,?,?)".replace("?,?,?,?,?", "?,?,?,?"),
                    (session_id, "room-local", "surface-local", json.dumps({"sessionId": session_id, "roomId": "room-local", "surfaceId": "surface-local"})),
                )
            row = self._db.execute(
                "SELECT consent_epoch FROM participants WHERE session_id=? AND peer_id=?",
                (session_id, peer_id),
            ).fetchone()
            epoch = int(row[0]) + 1 if row else 1
            if not allowed and row is not None:
                epoch += 1
            self._db.execute("INSERT INTO participants VALUES (?,?,?,?,?) ON CONFLICT(session_id,peer_id) DO UPDATE SET consent=excluded.consent, consent_epoch=excluded.consent_epoch, active_from=excluded.active_from", (session_id, peer_id, int(allowed), epoch, int(active_from_ms)))
            self._bump(session_id)
        return epoch

    def ingest(self, event: Mapping[str, Any], context: Mapping[str, Any], *, consent: bool | None = None) -> str:
        session_id = str(event["session_id"])
        peer_id = str(event["peer_id"])
        with self._db:
            session = self._db.execute("SELECT 1 FROM sessions WHERE session_id=?", (session_id,)).fetchone()
            if session is None:
                self._db.execute(
                    "INSERT INTO sessions(session_id,room_id,surface_id,context_json) VALUES (?,?,?,?)",
                    (session_id, str(context["roomId"]), str(context["surfaceId"]), json.dumps(dict(context), sort_keys=True)),
                )
            participant = self._db.execute(
                "SELECT consent, consent_epoch, active_from FROM participants WHERE session_id=? AND peer_id=?",
                (session_id, peer_id),
            ).fetchone()
            if participant is None:
                self._db.execute("INSERT INTO participants VALUES (?,?,?,?,?)", (session_id, peer_id, int(consent is True), 1, 0))
                participant = (int(consent is True), 1, 0)
            if self._db.execute("SELECT 1 FROM events WHERE event_id=?", (event["event_id"],)).fetchone():
                return "duplicate"
            accepted = bool(consent if consent is not None else participant[0])
            at_ms = _timestamp_ms(event["source_timestamp"])
            bridge = CanonicalEventBridge()
            bridge.ingest(event, context, consent=accepted)
            self._db.execute(
                "INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                (event["event_id"], session_id, peer_id, at_ms, int(participant[1]), int(accepted), json.dumps(dict(event), sort_keys=True)),
            )
            self._bump(session_id)
        return "accepted" if accepted else "blocked"

    def tick(self, session_id: str, now_ms: int) -> dict[str, Any]:
        with self._db:
            row = self._db.execute("SELECT logical_now FROM sessions WHERE session_id=?", (session_id,)).fetchone()
            if row is None:
                raise KeyError(session_id)
            logical_now = max(int(row[0]), int(now_ms))
            self._db.execute("UPDATE sessions SET logical_now=?, revision=revision+1 WHERE session_id=?", (logical_now, session_id))
        return self.snapshot(session_id, evaluation_ms=logical_now)

    def snapshot(self, session_id: str, *, evaluation_ms: int | None = None) -> dict[str, Any]:
        session = self._db.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        if session is None:
            raise KeyError(session_id)
        participants = self._db.execute("SELECT peer_id, consent_epoch, active_from FROM participants WHERE session_id=?", (session_id,)).fetchall()
        epochs = {str(row[0]): int(row[1]) for row in participants}
        active_from = {str(row[0]): int(row[2]) for row in participants}
        now = int(session["logical_now"] if evaluation_ms is None else evaluation_ms)
        rows = self._db.execute("SELECT * FROM events WHERE session_id=?", (session_id,)).fetchall()
        records = [dict(row) for row in rows]
        for record in records:
            record["active_from"] = active_from.get(str(record["peer_id"]), 0)
        visible = eligible_events(records, evaluation_ms=now, stale_after_ms=self.stale_after_ms, consent_epochs=epochs)
        events = [json.loads(row["event_json"]) for row in visible]
        context = json.loads(session["context_json"])
        replay = CanonicalEventReplay().run(events, context, consent=True) if events else CanonicalEventReplay().run([], context, consent=True)
        view = replay["finalPupilaView"] or _empty_view(session_id, context)
        lucida = project_pupila_for_lucida(view)
        return {"sessionId": session_id, "evaluationMs": now, "revision": int(session["revision"]), "eventCount": len(events), "pupilaView": view, "lucidaView": lucida, "renderPlan": build_lucida_render_plan(lucida)}

    def decide(self, session_id: str, proposal_id: str, *, request_id: str, revert_decision_id: str | None = None) -> dict[str, Any]:
        current = self.snapshot(session_id)
        proposal_ids = {item["proposalId"] for item in current["pupilaView"]["proposals"]}
        if proposal_id not in proposal_ids and revert_decision_id is None:
            raise ValueError("proposal is not currently eligible")
        existing = self._db.execute("SELECT * FROM decisions WHERE request_id=?", (request_id,)).fetchone()
        if existing:
            return dict(existing)
        decision_id = f"decision-{request_id}"
        with self._db:
            self._db.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?)", (decision_id, session_id, proposal_id, request_id, int(current["revision"]), "reverted" if revert_decision_id else "accepted", revert_decision_id))
        return dict(self._db.execute("SELECT * FROM decisions WHERE decision_id=?", (decision_id,)).fetchone())

    def _bump(self, session_id: str) -> None:
        self._db.execute("UPDATE sessions SET revision=revision+1 WHERE session_id=?", (session_id,))


def _timestamp_ms(value: str) -> int:
    from datetime import datetime
    return int(datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp() * 1000)


def _empty_view(session_id: str, context: Mapping[str, Any]) -> dict[str, Any]:
    from pupila_view import project_pupila_view
    return project_pupila_view({"sessionId": session_id, "roomId": context["roomId"], "surfaceId": context["surfaceId"], "participants": [], "proposals": []})


def _convert_view(view: Mapping[str, Any]) -> dict[str, Any]:
    """Adapt native camelCase PUPILA view to the established LUCIDA contract."""
    return {
        "contract_type": "LucidaOverlayView", "schema_version": "0.1", "surface": "LUCIDA", "mode": "read_only",
        "session_id": view["sessionId"], "phase": "temporal", "status": "observing" if view["participantCount"] else "created",
        "overlay_status": "proposal" if view["proposals"] else "ready", "capabilities": [{"capability": "pupila.shared-surface", "state": {"status": f"participants:{view['participantCount']}", "signal_status": "metadata-only"}, "observed_count": view["participantCount"], "expected_result_count": view["proposalCount"], "unknowns": []}],
        "pending_proposals": [{"proposal_id": item["proposalId"], "event_id": item["proposalId"], "phase": "temporal", "operation": "pupila.coordinate", "reason": item["reason"], "risk": "unknown", "requires_explicit_approval": True, "reversible": True, "execution_mode": "proposal_only"} for item in view["proposals"]],
        "unknowns": [], "next_attention": {"kind": "proposal" if view["proposals"] else "waiting", "id": view["nextAttention"].get("proposalId") or "phase-temporal", "reason": view["nextAttention"]["reason"]},
        "safety": {"proposal_only": True, "automatic_actions": False, "external_side_effects": False},
    }


__all__ = ["TemporalCoordinator"]
