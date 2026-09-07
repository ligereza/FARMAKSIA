from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping

SOURCE = Path(os.environ.get("FARMAKSIA_090_ROOT", r"C:\IA\FARMAXIA\experiments\090-farmaxia-adaptive-representation-layer")).resolve()
if not SOURCE.is_dir():
    raise RuntimeError(f"FARMAKSIA_090_ROOT no existe o no es un directorio: {SOURCE}")
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from canonical_event_bridge import CanonicalEventBridge, CanonicalEventError  # type: ignore
from canonical_event_bridge import CanonicalEventReplay  # type: ignore
from contracts import deterministic_id  # type: ignore
from lucida_render_plan import build_lucida_render_plan  # type: ignore
from pupila_lucida_projection import project_pupila_for_lucida  # type: ignore
from pupila_view import project_pupila_view  # type: ignore


class EngineError(ValueError):
    pass


def _hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


class PupilaEngine:
    """Persistent PUPILA coordinator layered over the FARMAKSIA 090 adapters."""

    def __init__(self, db_path: str | Path, *, clock=None, stale_after_ms: int = 300_000):
        self.db_path = str(db_path)
        if isinstance(stale_after_ms, bool) or not isinstance(stale_after_ms, int) or stale_after_ms < 1_000:
            raise EngineError("stale_after_ms must be an integer >= 1000")
        self.clock = clock or (lambda: int(time.time() * 1000))
        self.stale_after_ms = stale_after_ms
        self._lock = threading.RLock()
        self._runtime_cache: dict[str, dict[str, Any]] = {}
        self._init_db()

    def _connect(self):
        db = sqlite3.connect(self.db_path, timeout=5, isolation_level="IMMEDIATE")
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    @contextmanager
    def _connection(self):
        db = self._connect()
        try:
            yield db
            db.commit()
        except sqlite3.OperationalError as exc:
            db.rollback()
            raise EngineError(f"storage conflict: {exc}") from exc
        finally:
            db.close()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions(session_id TEXT PRIMARY KEY, context_json TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0, logical_now INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS participants(session_id TEXT NOT NULL, participant_ref TEXT NOT NULL, consent INTEGER NOT NULL, epoch_start INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(session_id,participant_ref));
            CREATE TABLE IF NOT EXISTS events(session_id TEXT NOT NULL, event_id TEXT NOT NULL, peer_id TEXT NOT NULL, sequence INTEGER NOT NULL, event_json TEXT NOT NULL, accepted INTEGER NOT NULL, status TEXT NOT NULL, reason TEXT, arrival INTEGER NOT NULL, PRIMARY KEY(session_id,event_id), UNIQUE(session_id,peer_id,sequence));
            CREATE TABLE IF NOT EXISTS proposals(proposal_id TEXT NOT NULL, session_id TEXT NOT NULL, version INTEGER NOT NULL, kind TEXT NOT NULL, reason TEXT NOT NULL, support_hash TEXT NOT NULL, support_json TEXT NOT NULL, state TEXT NOT NULL, effective_decision_id TEXT, created_revision INTEGER NOT NULL, updated_revision INTEGER NOT NULL, PRIMARY KEY(session_id,proposal_id,version));
            CREATE TABLE IF NOT EXISTS decisions(decision_id TEXT NOT NULL, session_id TEXT NOT NULL, proposal_id TEXT NOT NULL, proposal_version INTEGER NOT NULL, decision TEXT NOT NULL, effect TEXT NOT NULL, request_hash TEXT NOT NULL, revert_decision_id TEXT, created_revision INTEGER NOT NULL, PRIMARY KEY(session_id,decision_id));
            CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, type TEXT NOT NULL, payload_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS event_expirations(session_id TEXT NOT NULL, event_id TEXT NOT NULL, peer_id TEXT NOT NULL, expires_at INTEGER NOT NULL, PRIMARY KEY(session_id,event_id));
            CREATE INDEX IF NOT EXISTS idx_event_expirations_due ON event_expirations(session_id,expires_at);
            CREATE TABLE IF NOT EXISTS schema_meta(version INTEGER PRIMARY KEY);
            """)
            # Small migration for databases created by the first local slice.
            columns = {row[1] for row in db.execute("PRAGMA table_info(proposals)")}
            for name, definition in (("support_hash", "TEXT NOT NULL DEFAULT ''"), ("support_json", "TEXT NOT NULL DEFAULT '{}'"), ("effective_decision_id", "TEXT")):
                if name not in columns:
                    db.execute(f"ALTER TABLE proposals ADD COLUMN {name} {definition}")
            columns = {row[1] for row in db.execute("PRAGMA table_info(decisions)")}
            for name, definition in (("request_hash", "TEXT NOT NULL DEFAULT ''"), ("revert_decision_id", "TEXT")):
                if name not in columns:
                    db.execute(f"ALTER TABLE decisions ADD COLUMN {name} {definition}")
            session_columns = {row[1] for row in db.execute("PRAGMA table_info(sessions)")}
            if "logical_now" not in session_columns:
                db.execute("ALTER TABLE sessions ADD COLUMN logical_now INTEGER NOT NULL DEFAULT 0")
            schema = db.execute("SELECT MAX(version) FROM schema_meta").fetchone()[0]
            if schema is None:
                db.execute("INSERT INTO schema_meta(version) VALUES(3)")
            elif int(schema) < 3:
                db.execute("INSERT INTO schema_meta(version) VALUES(3)")
            elif int(schema) > 3:
                raise EngineError(f"unsupported local schema version: {schema}")
            db.execute("INSERT OR IGNORE INTO event_expirations(session_id,event_id,peer_id,expires_at) SELECT session_id,event_id,peer_id,0 FROM events WHERE accepted=1")
            for row in db.execute("SELECT session_id,event_id,event_json FROM events WHERE accepted=1 AND event_id IN (SELECT event_id FROM event_expirations WHERE expires_at=0)").fetchall():
                db.execute("UPDATE event_expirations SET expires_at=? WHERE session_id=? AND event_id=?", (self._event_time_ms(json.loads(row[2])) + self.stale_after_ms, row[0], row[1]))

    def _context(self, session_id: str, context: Mapping[str, Any] | None) -> dict[str, Any]:
        if not isinstance(session_id, str) or not session_id.strip():
            raise EngineError("sessionId is required")
        base = {"sessionId": session_id, "roomId": "atelier-local", "surfaceId": "lamina-01", "host": "replay", "task": "preparar-lamina"}
        if context:
            base.update(dict(context))
        base["sessionId"] = session_id
        return base

    def _ensure_session(self, db, session_id: str, context: Mapping[str, Any] | None = None, create: bool = True) -> dict[str, Any]:
        ctx = self._context(session_id, context)
        row = db.execute("SELECT context_json FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        if row is None:
            if not create:
                raise EngineError("unknown session")
            db.execute("INSERT INTO sessions(session_id,context_json) VALUES(?,?)", (session_id, json.dumps(ctx, sort_keys=True)))
            return ctx
        saved = json.loads(row[0])
        if context and (saved.get("roomId") != ctx.get("roomId") or saved.get("surfaceId") != ctx.get("surfaceId")):
            raise EngineError("context roomId/surfaceId conflicts with the session")
        return saved

    def _revision(self, db, session_id: str) -> int:
        return int(db.execute("SELECT revision FROM sessions WHERE session_id=?", (session_id,)).fetchone()[0])

    def _bump(self, db, session_id: str) -> int:
        db.execute("UPDATE sessions SET revision=revision+1 WHERE session_id=?", (session_id,))
        return self._revision(db, session_id)

    def _audit(self, db, session_id: str, kind: str, payload: Mapping[str, Any]):
        db.execute("INSERT INTO audit(session_id,type,payload_json) VALUES(?,?,?)", (session_id, kind, json.dumps(dict(payload), sort_keys=True)))

    def _safe_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        safe = dict(event)
        payload = event.get("payload") if isinstance(event.get("payload"), Mapping) else {}
        channel = str(event.get("channel", "")).lower()
        keys = {"focus": ("focused",), "pointer": ("x", "y"), "gaze": ("x", "y", "quality"), "keyboard": ("count", "shortcut"), "task": ("progress",), "presence": ("state",)}.get(channel, ())
        safe["payload"] = {key: payload[key] for key in keys if key in payload}
        return safe

    def _consent(self, db, session_id: str, peer_id: str):
        return db.execute("SELECT consent,epoch_start FROM participants WHERE session_id=? AND participant_ref=?", (session_id, peer_id)).fetchone()

    def _now_ms(self) -> int:
        now = self.clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise EngineError("clock must return milliseconds")
        return int(now)

    def _commit_clock(self, db, session_id: str, evaluation_ms: int | None = None) -> tuple[int, bool]:
        if evaluation_ms is not None and (isinstance(evaluation_ms, bool) or not isinstance(evaluation_ms, int)):
            raise EngineError("evaluationMs must be an integer in milliseconds")
        raw = self._now_ms() if evaluation_ms is None else evaluation_ms
        current = int(db.execute("SELECT logical_now FROM sessions WHERE session_id=?", (session_id,)).fetchone()[0])
        logical = max(raw, current)
        changed = logical > current
        if changed:
            db.execute("UPDATE sessions SET logical_now=? WHERE session_id=?", (logical, session_id))
        return logical, changed

    @staticmethod
    def _event_time_ms(event: Mapping[str, Any]) -> int:
        try:
            value = str(event["source_timestamp"]).replace("Z", "+00:00")
            return int(datetime.fromisoformat(value).astimezone(timezone.utc).timestamp() * 1000)
        except (KeyError, TypeError, ValueError) as exc:
            raise EngineError("event source_timestamp is not valid ISO-8601") from exc

    def _fresh_at(self, event: Mapping[str, Any], now_ms: int) -> bool:
        age = now_ms - self._event_time_ms(event)
        return 0 <= age <= self.stale_after_ms

    def ingest_event(self, event: Mapping[str, Any], context: Mapping[str, Any] | None = None, consent: bool | None = None, *, _reconcile: bool = True, _include_state: bool = True) -> dict[str, Any]:
        with self._lock, self._connection() as db:
            if not isinstance(event, Mapping):
                raise EngineError("event must be an object")
            session_id, peer_id = event.get("session_id"), event.get("peer_id")
            if not isinstance(session_id, str) or not session_id or not isinstance(peer_id, str) or not peer_id:
                raise EngineError("event session_id and peer_id are required")
            self._ensure_session(db, session_id, context)
            event_id = event.get("event_id")
            prior = db.execute("SELECT status,reason FROM events WHERE session_id=? AND event_id=?", (session_id, event_id)).fetchone()
            if prior:
                return {"status": "duplicate", "eventId": event_id, "reason": prior[1]}
            if consent is not None and not isinstance(consent, bool):
                raise EngineError("consent must be boolean or omitted")
            row = self._consent(db, session_id, peer_id)
            if row is None:
                persisted_consent = consent is True
                arrival = int(db.execute("SELECT COALESCE(MAX(arrival),0)+1 FROM events").fetchone()[0])
                db.execute("INSERT INTO participants VALUES(?,?,?,?)", (session_id, peer_id, int(persisted_consent), arrival))
                row = (int(persisted_consent), arrival)
            consent_value = bool(row[0]) if consent is None else consent and bool(row[0])
            sequence = event.get("sequence")
            if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
                raise EngineError("sequence must be a positive integer")
            latest = db.execute("SELECT MAX(sequence) FROM events WHERE session_id=? AND peer_id=?", (session_id, peer_id)).fetchone()[0]
            if latest is not None and sequence <= int(latest):
                try:
                    CanonicalEventBridge().ingest(event, self._context(session_id, context), consent=consent_value)
                except (CanonicalEventError, ValueError) as exc:
                    raise EngineError(str(exc)) from exc
                return {"status": "out_of_order", "eventId": event_id, "reason": "sequence-not-greater-than-latest", "revision": self._revision(db, session_id)}
            status, reason = ("blocked", "consent-required-or-revoked") if not consent_value else ("accepted", None)
            try:
                CanonicalEventBridge().ingest(event, self._context(session_id, context), consent=consent_value)
            except (CanonicalEventError, ValueError) as exc:
                raise EngineError(str(exc)) from exc
            self._commit_clock(db, session_id)
            arrival = int(db.execute("SELECT COALESCE(MAX(arrival),0)+1 FROM events").fetchone()[0])
            safe_event = self._safe_event(event)
            db.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)", (session_id, event_id, peer_id, sequence, json.dumps(safe_event, sort_keys=True), int(status == "accepted"), status, reason, arrival))
            if status == "accepted":
                db.execute("INSERT INTO event_expirations VALUES(?,?,?,?)", (session_id, event_id, peer_id, self._event_time_ms(safe_event) + self.stale_after_ms))
            revision = self._bump(db, session_id)
            self._audit(db, session_id, "event.ingested", {"eventId": event_id, "peerId": peer_id, "sequence": sequence, "status": status, "revision": revision})
            if status == "accepted" and _reconcile:
                self._reconcile_locked(db, session_id)
            result = {"status": status, "eventId": event_id, "reason": reason, "revision": revision}
            if _include_state:
                result["state"] = self._snapshot_locked(db, session_id)
            return result

    def ingest_batch(self, events: list[Mapping[str, Any]], context: Mapping[str, Any] | None = None, consent_by_participant: Mapping[str, bool] | None = None) -> list[dict[str, Any]]:
        if not isinstance(events, list):
            raise EngineError("events must be a list")
        # Partial acceptance is explicit: supplied order is causal order; each
        # result carries its own status and later items still get evaluated.
        results = []
        sessions: set[str] = set()
        for event in events:
            try:
                result = self.ingest_event(event, context, (consent_by_participant or {}).get(event.get("peer_id")), _reconcile=False, _include_state=False)
                results.append(result)
                if result["status"] == "accepted" and isinstance(event, Mapping) and isinstance(event.get("session_id"), str): sessions.add(event["session_id"])
            except EngineError as exc:
                results.append({"status": "rejected", "eventId": event.get("event_id") if isinstance(event, Mapping) else None, "reason": str(exc)})
        for session_id in sessions:
            self.reconcile(session_id)
        return results

    def reconcile(self, session_id: str) -> dict[str, Any]:
        with self._lock, self._connection() as db:
            self._ensure_session(db, session_id, create=False)
            _, advanced = self._commit_clock(db, session_id)
            self._reconcile_locked(db, session_id, publish_temporal=advanced)
            return self._snapshot_locked(db, session_id)

    def tick(self, session_id: str, evaluation_ms: int | None = None) -> dict[str, Any]:
        """Evaluate time-based freshness and persist any invalidation."""
        with self._lock, self._connection() as db:
            self._ensure_session(db, session_id, create=False)
            _, advanced = self._commit_clock(db, session_id, evaluation_ms)
            self._reconcile_locked(db, session_id, publish_temporal=advanced)
            return self._snapshot_locked(db, session_id)

    def set_consent(self, session_id: str, participant_ref: str, consent: bool, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if not isinstance(participant_ref, str) or not participant_ref.strip() or not isinstance(consent, bool):
            raise EngineError("participantRef must be non-empty and consent must be boolean")
        with self._lock, self._connection() as db:
            self._ensure_session(db, session_id, context)
            _, advanced = self._commit_clock(db, session_id)
            row = self._consent(db, session_id, participant_ref)
            if row and bool(row[0]) == consent:
                self._reconcile_locked(db, session_id, publish_temporal=advanced)
                return {"status": "unchanged", "revision": self._revision(db, session_id), "state": self._snapshot_locked(db, session_id)}
            epoch = int(db.execute("SELECT COALESCE(MAX(arrival),0)+1 FROM events").fetchone()[0])
            if row is None: db.execute("INSERT INTO participants VALUES(?,?,?,?)", (session_id, participant_ref, int(consent), epoch))
            else: db.execute("UPDATE participants SET consent=?,epoch_start=? WHERE session_id=? AND participant_ref=?", (int(consent), epoch, session_id, participant_ref))
            revision = self._bump(db, session_id)
            self._audit(db, session_id, "consent.changed", {"participantRef": participant_ref, "consent": consent, "revision": revision})
            self._reconcile_locked(db, session_id)
            return {"status": "consent_updated", "revision": revision, "state": self._snapshot_locked(db, session_id)}

    def _runtime(self, db, session_id: str, context: Mapping[str, Any], evaluation_ms: int | None = None) -> dict[str, Any]:
        latest_rows = db.execute("SELECT peer_id,MAX(arrival),COUNT(*) FROM events WHERE session_id=? AND accepted=1 GROUP BY peer_id ORDER BY peer_id", (session_id,)).fetchall()
        consent_rows = db.execute("SELECT participant_ref,consent,epoch_start FROM participants WHERE session_id=? ORDER BY participant_ref", (session_id,)).fetchall()
        consent_signature = [(row[0], row[1], row[2]) for row in consent_rows]
        if evaluation_ms is not None and (isinstance(evaluation_ms, bool) or not isinstance(evaluation_ms, int)):
            raise EngineError("evaluationMs must be an integer in milliseconds")
        raw_now_ms = self._now_ms() if evaluation_ms is None else evaluation_ms
        durable_now_ms = int(db.execute("SELECT logical_now FROM sessions WHERE session_id=?", (session_id,)).fetchone()[0])
        previous = self._runtime_cache.get(session_id)
        now_ms = max(raw_now_ms, durable_now_ms, int(previous["evaluatedAtMs"]) if previous else raw_now_ms)
        latest_by_peer = {row[0]: json.loads(row[1]) for row in db.execute("SELECT e.peer_id,e.event_json FROM events e JOIN (SELECT peer_id,MAX(arrival) AS max_arrival FROM events WHERE session_id=? AND accepted=1 GROUP BY peer_id) latest ON e.peer_id=latest.peer_id AND e.arrival=latest.max_arrival WHERE e.session_id=?", (session_id, session_id)).fetchall()}
        consent_by_peer = {row[0]: row for row in consent_rows}
        temporal_signature = [(row[0], row[1], row[2], bool(consent_by_peer.get(row[0]) and int(consent_by_peer[row[0]][1]) == 1), self._fresh_at(latest_by_peer[row[0]], now_ms) if row[0] in latest_by_peer else False) for row in latest_rows]
        signature = _hash({"latest": [(row[0], row[1], row[2]) for row in latest_rows], "consent": consent_signature, "temporal": temporal_signature})
        next_expiry = db.execute("SELECT MIN(expires_at) FROM event_expirations WHERE session_id=? AND expires_at>?", (session_id, now_ms)).fetchone()[0]
        if evaluation_ms is None and previous and previous["signature"] == signature and now_ms < int(previous["validUntilMs"]):
            result = previous["result"]
            result["temporal"] = {"nowMs": now_ms, "rawNowMs": raw_now_ms, "clockRewindClamped": raw_now_ms < now_ms, "staleAfterMs": self.stale_after_ms, "activeParticipants": sorted(row[0] for row in temporal_signature if row[3] and row[4]), "staleParticipants": sorted(row[0] for row in temporal_signature if row[3] and not row[4])}
            return result
        rows = db.execute("SELECT event_json,peer_id,arrival FROM events WHERE session_id=? AND accepted=1 ORDER BY arrival", (session_id,)).fetchall()
        eligible = []
        for row in rows:
            event = json.loads(row[0]); consent = self._consent(db, session_id, row[1])
            fresh = self._fresh_at(event, now_ms)
            if consent and int(consent[0]) == 1 and int(row[2]) >= int(consent[1]) and fresh:
                eligible.append(event)
        result = CanonicalEventReplay().run(eligible, context, consent=True)
        result["temporal"] = {"nowMs": now_ms, "rawNowMs": raw_now_ms, "clockRewindClamped": raw_now_ms < now_ms, "staleAfterMs": self.stale_after_ms, "activeParticipants": sorted(row[0] for row in temporal_signature if row[3] and row[4]), "staleParticipants": sorted(row[0] for row in temporal_signature if row[3] and not row[4]), "nextExpiryMs": next_expiry}
        if evaluation_ms is None:
            self._runtime_cache[session_id] = {"signature": signature, "evaluatedAtMs": now_ms, "validUntilMs": int(next_expiry or now_ms + self.stale_after_ms), "result": result}
        return result

    def _reconcile_locked(self, db, session_id: str, *, publish_temporal: bool = False):
        before = {row[0]: row[1] for row in db.execute("SELECT proposal_id,state FROM proposals WHERE session_id=? AND state IN ('proposed','accepted','reverted_to_proposed')", (session_id,)).fetchall()}
        context = json.loads(db.execute("SELECT context_json FROM sessions WHERE session_id=?", (session_id,)).fetchone()[0])
        replay = self._runtime(db, session_id, context)
        raws = replay.get("finalPupilaState", {}).get("proposals", []) if replay.get("finalPupilaState") else []
        participants = replay.get("finalPupilaView", {}).get("participants", []) if replay.get("finalPupilaView") else []
        participant_refs = tuple(sorted(p["participantRef"] for p in participants))
        candidates = {(raw["kind"], participant_refs): {**raw, "reason": "participants expose different rendering policies; a shared next step is proposed" if raw["kind"] == "peer-bridge" else raw["reason"]} for raw in raws}
        help_events = []
        now_ms = replay.get("temporal", {}).get("nowMs", self._now_ms())
        for event_json, peer_id, arrival in db.execute("SELECT event_json,peer_id,arrival FROM events WHERE session_id=? AND accepted=1 ORDER BY arrival", (session_id,)).fetchall():
            event = json.loads(event_json)
            consent = self._consent(db, session_id, peer_id)
            if consent and int(consent[0]) == 1 and int(arrival) >= int(consent[1]) and self._fresh_at(event, now_ms) and event.get("event_type") == "task.help_requested":
                help_events.append(event)
        for help_event in help_events:
            if participant_refs:
                request_id = str(help_event.get("event_id"))
                candidates[(f"explicit-help:{request_id}", participant_refs)] = {"kind": "explicit-help", "requestId": request_id, "reason": "a participant explicitly requested a shared next step", "proposalId": request_id}
        for (kind, refs), raw in candidates.items():
            temporal = replay.get("temporal", {})
            semantic_support = {"kind": raw["kind"], "participants": [{"participantRef": p["participantRef"], "policy": p["policy"], "focusState": p["focusState"], "signalCoverage": p["interaction"]["signalCoverage"]} for p in participants], "reason": raw["reason"], "activeParticipants": temporal.get("activeParticipants", []), "staleParticipants": temporal.get("staleParticipants", [])}
            if raw.get("requestId"):
                semantic_support["requestId"] = raw["requestId"]
            proposal_id = deterministic_id("pupila-proposal", {"sessionId": session_id, "surfaceId": context["surfaceId"], "kind": kind, "participants": refs})
            support_hash = _hash(semantic_support)
            latest = db.execute("SELECT version,support_hash,state FROM proposals WHERE session_id=? AND proposal_id=? ORDER BY version DESC LIMIT 1", (session_id, proposal_id)).fetchone()
            if latest and latest[1] == support_hash and latest[2] not in {"invalidated", "superseded"}:
                continue
            if latest and latest[2] in {"proposed", "accepted", "reverted_to_proposed"}:
                db.execute("UPDATE proposals SET state='superseded',effective_decision_id=NULL,updated_revision=? WHERE session_id=? AND proposal_id=? AND version=?", (self._revision(db, session_id), session_id, proposal_id, latest[0]))
            version = int(latest[0]) + 1 if latest else 1
            rev = self._revision(db, session_id)
            db.execute("INSERT INTO proposals(proposal_id,session_id,version,kind,reason,support_hash,support_json,state,effective_decision_id,created_revision,updated_revision) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (proposal_id, session_id, version, raw["kind"], raw["reason"], support_hash, json.dumps(semantic_support, sort_keys=True), "proposed", None, rev, rev))
        current_ids = {deterministic_id("pupila-proposal", {"sessionId": session_id, "surfaceId": context["surfaceId"], "kind": kind, "participants": refs}) for kind, refs in candidates}
        if not current_ids:
            db.execute("UPDATE proposals SET state='invalidated',updated_revision=? WHERE session_id=? AND state IN ('proposed','accepted','reverted_to_proposed')", (self._revision(db, session_id), session_id))
        else:
            placeholders = ",".join("?" for _ in current_ids)
            db.execute(f"UPDATE proposals SET state='invalidated',effective_decision_id=NULL,updated_revision=? WHERE session_id=? AND state IN ('proposed','accepted','reverted_to_proposed') AND proposal_id NOT IN ({placeholders})", (self._revision(db, session_id), session_id, *current_ids))
        if publish_temporal:
            after = {row[0]: row[1] for row in db.execute("SELECT proposal_id,state FROM proposals WHERE session_id=? AND state IN ('proposed','accepted','reverted_to_proposed')", (session_id,)).fetchall()}
            if before != after:
                revision = self._bump(db, session_id)
                db.execute("UPDATE proposals SET updated_revision=? WHERE session_id=? AND updated_revision<? AND state IN ('invalidated','proposed','accepted','reverted_to_proposed')", (revision, session_id, revision))
                self._audit(db, session_id, "temporal.reconciled", {"revision": revision, "evaluatedAtMs": replay.get("temporal", {}).get("nowMs"), "nextExpiryMs": replay.get("temporal", {}).get("nextExpiryMs")})

    def decide(self, session_id: str, proposal_id: str, proposal_version: int, decision: str, decision_id: str, context: Mapping[str, Any] | None = None, revert_decision_id: str | None = None) -> dict[str, Any]:
        if not all(isinstance(x, str) and x.strip() for x in (session_id, proposal_id, decision_id)) or not isinstance(proposal_version, int) or proposal_version < 1:
            raise EngineError("session, proposal, decision ID and positive version are required")
        if decision not in {"accept", "reject", "revert"}: raise EngineError("decision must be accept, reject or revert")
        with self._lock, self._connection() as db:
            self._ensure_session(db, session_id, context, create=False)
            _, advanced = self._commit_clock(db, session_id)
            # A decision is evaluated against the current derived state. This
            # makes a stale proposal non-actionable even when the caller did
            # not issue an explicit tick first.
            self._reconcile_locked(db, session_id, publish_temporal=advanced)
            request_hash = _hash({"sessionId": session_id, "proposalId": proposal_id, "proposalVersion": proposal_version, "decision": decision, "revertDecisionId": revert_decision_id})
            old = db.execute("SELECT request_hash,decision,effect FROM decisions WHERE session_id=? AND decision_id=?", (session_id, decision_id)).fetchone()
            if old:
                if old[0] != request_hash: raise EngineError("decisionId conflict: same key used for another request")
                return {"status": "duplicate_decision", "decision": old[1], "effect": old[2], "state": self._snapshot_locked(db, session_id)}
            proposal = db.execute("SELECT state,effective_decision_id FROM proposals WHERE session_id=? AND proposal_id=? AND version=?", (session_id, proposal_id, proposal_version)).fetchone()
            if proposal is None: raise EngineError("proposal does not exist in this session and version")
            current, effective_decision_id = proposal[0], proposal[1]
            if decision == "revert":
                if not isinstance(revert_decision_id, str) or not revert_decision_id: raise EngineError("revertDecisionId is required")
                valid = db.execute("SELECT 1 FROM decisions WHERE session_id=? AND decision_id=? AND proposal_id=? AND proposal_version=? AND decision='accept' AND effect='accepted'", (session_id, revert_decision_id, proposal_id, proposal_version)).fetchone()
                if not valid or current != "accepted" or effective_decision_id != revert_decision_id: raise EngineError("accepted decision is not currently effective or cannot be reverted")
                new_state, effect = "proposed", "reverted_to_proposed"
            elif current != "proposed": raise EngineError("proposal is not currently actionable")
            else: new_state, effect = ("accepted", "accepted") if decision == "accept" else ("rejected", "rejected")
            revision = self._bump(db, session_id)
            expected_state = "accepted" if decision == "revert" else "proposed"
            next_effective = decision_id if decision == "accept" else None
            changed = db.execute("UPDATE proposals SET state=?,effective_decision_id=?,updated_revision=? WHERE session_id=? AND proposal_id=? AND version=? AND state=?", (new_state, next_effective, revision, session_id, proposal_id, proposal_version, expected_state)).rowcount
            if changed != 1:
                raise EngineError("proposal changed concurrently; retry with a fresh snapshot")
            db.execute("INSERT INTO decisions(decision_id,session_id,proposal_id,proposal_version,decision,effect,request_hash,revert_decision_id,created_revision) VALUES(?,?,?,?,?,?,?,?,?)", (decision_id, session_id, proposal_id, proposal_version, decision, effect, request_hash, revert_decision_id, revision))
            self._audit(db, session_id, "proposal.decided", {"proposalId": proposal_id, "version": proposal_version, "decisionId": decision_id, "decision": decision, "effect": effect, "revertDecisionId": revert_decision_id, "revision": revision})
            return {"status": "applied", "decision": decision, "effect": effect, "revision": revision, "state": self._snapshot_locked(db, session_id)}

    def _snapshot_locked(self, db, session_id: str, evaluation_ms: int | None = None) -> dict[str, Any]:
        context = json.loads(db.execute("SELECT context_json FROM sessions WHERE session_id=?", (session_id,)).fetchone()[0])
        replay = self._runtime(db, session_id, context, evaluation_ms)
        # Cached replay data is immutable from the snapshot's perspective.
        # Copy before replacing proposal state so a later decision cannot
        # mutate an earlier "before" view held by an integration consumer.
        view = json.loads(json.dumps(replay["finalPupilaView"], sort_keys=True)) if replay.get("finalPupilaView") else project_pupila_view({"sessionId": session_id, "roomId": context["roomId"], "surfaceId": context["surfaceId"], "participants": [], "proposals": []})
        state = replay.get("finalPupilaState") or {}
        rows = db.execute("SELECT proposal_id,version,kind,reason,state,support_hash,support_json FROM proposals WHERE session_id=? AND state='proposed' ORDER BY updated_revision DESC LIMIT 8", (session_id,)).fetchall() if state.get("proposals") else []
        view["proposals"] = [{"proposalId": r[0], "kind": r[2], "reason": r[3], "state": r[4], "requiresExplicitAcceptance": True, "reversible": True} for r in rows]
        view["proposalCount"] = len(view["proposals"]); view["shownProposalCount"] = len(view["proposals"])
        lucida = project_pupila_for_lucida(view, phase="preparation")
        plan = build_lucida_render_plan(lucida)
        history = []
        for row in db.execute("SELECT type,payload_json FROM audit WHERE session_id=? ORDER BY seq", (session_id,)).fetchall(): history.append({"type": row[0], "payload": json.loads(row[1])})
        proposals = [{"proposalId": r[0], "version": r[1], "kind": r[2], "reason": r[3], "state": r[4], "supportHash": r[5], "support": json.loads(r[6])} for r in db.execute("SELECT proposal_id,version,kind,reason,state,support_hash,support_json FROM proposals WHERE session_id=? ORDER BY CASE WHEN state='proposed' THEN 0 ELSE 1 END,updated_revision DESC", (session_id,)).fetchall()]
        return {"context": context, "source": {"mode": "persistent-replay", "label": "Motor local persistente; señales sintéticas declaradas"}, "replay": replay, "pupila": view, "lucida": lucida, "renderPlan": plan, "proposals": proposals, "history": history, "revision": self._revision(db, session_id)}

    def snapshot(self, session_id: str, evaluation_ms: int | None = None) -> dict[str, Any]:
        with self._lock, self._connection() as db:
            self._ensure_session(db, session_id, create=False)
            return self._snapshot_locked(db, session_id, evaluation_ms)
