from __future__ import annotations

import copy
import json
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.pupila_engine import CanonicalEventReplay, EngineError, PupilaEngine
from app.temporal_reference import evaluate_temporal_reference
from app.server import CONTEXT, EVENTS


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmps = []
        self.now = [1788724810000]

    def engine(self):
        tmp = tempfile.TemporaryDirectory()
        self.tmps.append(tmp)
        return PupilaEngine(Path(tmp.name) / "state.sqlite3", clock=lambda: self.now[0], stale_after_ms=10_000)

    def tearDown(self):
        for tmp in self.tmps:
            tmp.cleanup()

    def seeded(self, engine, session="pupila-demo"):
        events = copy.deepcopy(EVENTS)
        if session != "pupila-demo":
            for event in events:
                event["session_id"] = session
                event["event_id"] = f"{event['event_id']}-{session}"
            ctx = {**CONTEXT, "sessionId": session}
        else:
            ctx = CONTEXT
        engine.ingest_batch(events, ctx, {"participant-a": True, "participant-b": True})
        return engine.snapshot(session)

    def test_batch_and_incremental_are_semantically_equivalent(self):
        batch = self.engine(); a = self.seeded(batch)
        incremental = self.engine()
        for event in sorted(copy.deepcopy(EVENTS), key=lambda e: (e["peer_id"], e["sequence"])):
            incremental.ingest_event(event, CONTEXT, True)
        b = incremental.snapshot("pupila-demo")
        self.assertEqual(a["pupila"], b["pupila"])
        self.assertEqual(a["renderPlan"], b["renderPlan"])

    def test_invalid_duplicate_and_out_of_order_are_not_accepted(self):
        engine = self.engine()
        first = copy.deepcopy(EVENTS[0]); self.assertEqual(engine.ingest_event(first, CONTEXT, True)["status"], "accepted")
        self.assertEqual(engine.ingest_event(first, CONTEXT, True)["status"], "duplicate")
        older = copy.deepcopy(EVENTS[0]); older["event_id"] = "older-new-id"; older["sequence"] = 0
        with self.assertRaises(EngineError): engine.ingest_event(older, CONTEXT, True)
        collision = copy.deepcopy(EVENTS[0]); collision["event_id"] = "collision-new-id"; self.assertEqual(engine.ingest_event(collision, CONTEXT, True)["status"], "out_of_order")
        malformed = copy.deepcopy(EVENTS[0]); malformed["event_id"] = "bad"; malformed.pop("source_timestamp")
        with self.assertRaises(EngineError): engine.ingest_event(malformed, CONTEXT, True)

    def test_malformed_event_does_not_commit_logical_clock(self):
        engine = self.engine()
        malformed = copy.deepcopy(EVENTS[0]); malformed.pop("source_timestamp")
        with self.assertRaises(EngineError):
            engine.ingest_event(malformed, CONTEXT, True)
        db = sqlite3.connect(engine.db_path)
        try:
            row = db.execute("SELECT logical_now FROM sessions WHERE session_id='pupila-demo'").fetchone()
        finally:
            db.close()
        self.assertTrue(row is None or row[0] == 0)

    def test_lifecycle_changes_projection_and_reverts_effect(self):
        engine = self.engine(); initial = self.seeded(engine)
        proposal = initial["proposals"][0]
        accepted = engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "accept", "decision-accept-1")
        self.assertEqual(accepted["effect"], "accepted")
        after_accept = accepted["state"]
        self.assertEqual(after_accept["pupila"]["proposalCount"], 0)
        self.assertNotEqual(initial["renderPlan"]["viewDigest"], after_accept["renderPlan"]["viewDigest"])
        duplicate = engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "accept", "decision-accept-1")
        self.assertEqual(duplicate["status"], "duplicate_decision")
        reverted = engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "revert", "decision-revert-1", revert_decision_id="decision-accept-1")
        self.assertEqual(reverted["effect"], "reverted_to_proposed")
        self.assertEqual(reverted["state"]["pupila"]["proposalCount"], 1)
        with self.assertRaises(EngineError): engine.decide("pupila-demo", "missing", 1, "accept", "bad-id")

    def test_reject_is_not_revert_and_old_revision_conflicts(self):
        engine = self.engine(); state = self.seeded(engine); proposal = state["proposals"][0]
        rejected = engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "reject", "decision-reject-1")
        self.assertEqual(rejected["effect"], "rejected")
        with self.assertRaises(EngineError): engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "revert", "decision-revert-rejected")
        with self.assertRaises(EngineError): engine.decide("pupila-demo", proposal["proposalId"], 99, "accept", "decision-old-version")

    def test_persistence_consent_and_session_isolation(self):
        engine = self.engine(); before = self.seeded(engine)
        db_path = engine.db_path
        restarted = PupilaEngine(db_path, clock=lambda: self.now[0], stale_after_ms=10_000)
        self.assertEqual(before["pupila"], restarted.snapshot("pupila-demo")["pupila"])
        revoked = restarted.set_consent("pupila-demo", "participant-a", False)
        self.assertEqual(revoked["state"]["pupila"]["participantCount"], 1)
        after_revoke = copy.deepcopy(EVENTS[0]); after_revoke.update({"event_id": "evt-a-during-revoke", "sequence": 6, "source_timestamp": "2026-09-06T20:00:07+00:00", "received_timestamp": "2026-09-06T20:00:07+00:00"})
        self.assertEqual(restarted.ingest_event(after_revoke, CONTEXT, True)["status"], "blocked")
        restarted.set_consent("pupila-demo", "participant-a", True)
        after_regrant = copy.deepcopy(after_revoke); after_regrant.update({"event_id": "evt-a-after-regrant", "sequence": 7, "source_timestamp": "2026-09-06T20:00:08+00:00", "received_timestamp": "2026-09-06T20:00:08+00:00"})
        self.assertEqual(restarted.ingest_event(after_regrant, CONTEXT, True)["status"], "accepted")
        self.assertEqual(restarted.snapshot("pupila-demo")["pupila"]["participantCount"], 2)
        with self.assertRaises(EngineError): restarted.snapshot("other-session")
        with self.assertRaises(EngineError): restarted.decide("other-session", before["proposals"][0]["proposalId"], 1, "accept", "cross-session")
        self.assertEqual(restarted.ingest_event(copy.deepcopy(EVENTS[0]), CONTEXT, True)["status"], "duplicate")

    def test_revocation_invalidates_cause_and_cannot_be_accepted_or_reverted(self):
        engine = self.engine(); before = self.seeded(engine); proposal = next(p for p in before["proposals"] if p["state"] == "proposed")
        revoked = engine.set_consent("pupila-demo", "participant-b", False)
        self.assertEqual(revoked["state"]["pupila"]["participantCount"], 1)
        self.assertEqual(revoked["state"]["pupila"]["proposalCount"], 0)
        with self.assertRaises(EngineError): engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "accept", "revoked-accept")
        with self.assertRaises(EngineError): engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "revert", "revoked-revert", revert_decision_id="cycle-accept")

    def test_real_version_idempotency_conflict_and_pure_snapshot(self):
        engine = self.engine(); first = self.seeded(engine); p1 = next(p for p in first["proposals"] if p["state"] == "proposed"); revision = first["revision"]
        self.assertEqual(engine.snapshot("pupila-demo")["revision"], revision)
        new_event = copy.deepcopy(EVENTS[0]); new_event.update({"event_id": "evt-a-new-evidence", "sequence": 6, "payload": {"focused": False}, "source_timestamp": "2026-09-06T20:00:07+00:00", "received_timestamp": "2026-09-06T20:00:07+00:00"})
        changed = engine.ingest_event(new_event, CONTEXT, None)["state"]
        p2 = next(p for p in changed["proposals"] if p["state"] == "proposed")
        self.assertEqual(p2["version"], p1["version"] + 1)
        self.assertNotEqual(p1["supportHash"], p2["supportHash"])
        accepted = engine.decide("pupila-demo", p2["proposalId"], p2["version"], "accept", "same-key")
        self.assertEqual(accepted["effect"], "accepted")
        with self.assertRaises(EngineError): engine.decide("pupila-demo", "invented", 99, "reject", "same-key")

    def test_pointer_noise_does_not_reopen_and_old_accept_cannot_rollback_new_accept(self):
        engine = self.engine(); first = self.seeded(engine); p1 = next(p for p in first["proposals"] if p["state"] == "proposed")
        accepted = engine.decide("pupila-demo", p1["proposalId"], p1["version"], "accept", "accept-1")
        noise = copy.deepcopy(EVENTS[5]); noise.update({"event_id": "pointer-noise", "sequence": 6, "source_timestamp": "2026-09-06T20:00:07+00:00", "received_timestamp": "2026-09-06T20:00:07+00:00"})
        after_noise = engine.ingest_event(noise, CONTEXT, None)["state"]
        self.assertEqual(after_noise["pupila"]["proposalCount"], 0)
        new_event = copy.deepcopy(EVENTS[0]); new_event.update({"event_id": "focus-relevant-change", "sequence": 7, "payload": {"focused": False}, "source_timestamp": "2026-09-06T20:00:08+00:00", "received_timestamp": "2026-09-06T20:00:08+00:00"})
        changed = engine.ingest_event(new_event, CONTEXT, None)["state"]
        self.assertEqual(changed["pupila"]["proposalCount"], 1)
        p2 = next(p for p in changed["proposals"] if p["state"] == "proposed")
        self.assertEqual(p2["version"], p1["version"] + 1)
        engine.decide("pupila-demo", p2["proposalId"], p2["version"], "accept", "accept-2")
        with self.assertRaises(EngineError): engine.decide("pupila-demo", p2["proposalId"], p2["version"], "revert", "old-rollback", revert_decision_id="accept-1")

    def test_partial_batch_keeps_per_item_result_and_two_instances_share_state(self):
        engine = self.engine(); first = copy.deepcopy(EVENTS[0]); malformed = copy.deepcopy(EVENTS[1]); malformed["event_id"] = "malformed-mid"; malformed.pop("source_timestamp"); third = copy.deepcopy(EVENTS[2]); third["event_id"] = "third-after-gap"; third["sequence"] = 2; third["peer_id"] = first["peer_id"]; third["source_timestamp"] = "2026-09-06T20:00:02+00:00"; third["received_timestamp"] = third["source_timestamp"]
        results = engine.ingest_batch([first, malformed, third], CONTEXT, {"participant-a": True, "participant-b": True})
        self.assertEqual([item["status"] for item in results], ["accepted", "rejected", "accepted"])
        other = PupilaEngine(engine.db_path, clock=lambda: self.now[0], stale_after_ms=10_000); self.assertEqual(other.snapshot("pupila-demo")["replay"]["acceptedCount"], 2)

    def test_two_instances_compete_without_double_decision(self):
        engine = self.engine(); state = self.seeded(engine); proposal = next(p for p in state["proposals"] if p["state"] == "proposed")
        left, right = PupilaEngine(engine.db_path, clock=lambda: self.now[0], stale_after_ms=10_000), PupilaEngine(engine.db_path, clock=lambda: self.now[0], stale_after_ms=10_000)
        def decide(instance, decision, key):
            try:
                return instance.decide("pupila-demo", proposal["proposalId"], proposal["version"], decision, key)["status"]
            except EngineError:
                return "conflict"
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = sorted(pool.map(lambda args: decide(*args), ((left, "accept", "race-a"), (right, "reject", "race-b"))))
        self.assertEqual(outcomes, ["applied", "conflict"])

    def test_schema_migration_is_explicit_and_non_destructive(self):
        tmp = tempfile.TemporaryDirectory(); self.tmps.append(tmp); path = Path(tmp.name) / "legacy.sqlite3"
        db = sqlite3.connect(path)
        try:
            db.executescript("CREATE TABLE proposals(proposal_id TEXT,session_id TEXT,version INTEGER,kind TEXT,reason TEXT,state TEXT,created_revision INTEGER,updated_revision INTEGER,PRIMARY KEY(session_id,proposal_id,version)); CREATE TABLE decisions(decision_id TEXT,session_id TEXT,proposal_id TEXT,proposal_version INTEGER,decision TEXT,effect TEXT,created_revision INTEGER,PRIMARY KEY(session_id,decision_id)); INSERT INTO proposals VALUES('legacy','s',1,'co-presence','old','rejected',1,1);")
            db.commit()
        finally: db.close()
        PupilaEngine(path)
        db = sqlite3.connect(path)
        try:
            proposal_columns = {row[1] for row in db.execute("PRAGMA table_info(proposals)")}; version = db.execute("SELECT version FROM schema_meta").fetchone()[0]; preserved = db.execute("SELECT reason FROM proposals WHERE proposal_id='legacy'").fetchone()[0]
        finally: db.close()
        self.assertTrue({"support_hash", "support_json", "effective_decision_id"}.issubset(proposal_columns)); self.assertEqual(version, 3); self.assertEqual(preserved, "old")

    def test_time_tick_marks_silence_as_stale_and_withdraws_projection(self):
        engine = self.engine(); fresh = self.seeded(engine); self.assertEqual(fresh["pupila"]["proposalCount"], 1)
        self.now[0] = 1788724830000
        preview = engine.snapshot("pupila-demo")
        self.assertEqual(preview["pupila"]["proposalCount"], 0)
        self.assertEqual(set(preview["replay"]["temporal"]["staleParticipants"]), {"participant-a", "participant-b"})
        ticked = engine.tick("pupila-demo")
        self.assertEqual(ticked["pupila"]["proposalCount"], 0)
        self.assertEqual(ticked["revision"], fresh["revision"] + 1)
        self.assertTrue(any(p["state"] == "invalidated" for p in ticked["proposals"]))
        restarted = PupilaEngine(engine.db_path, clock=lambda: 1788724810000, stale_after_ms=10_000)
        recovered = restarted.tick("pupila-demo")
        self.assertEqual(recovered["pupila"]["proposalCount"], 0)
        self.assertEqual(recovered["revision"], ticked["revision"])

    def test_explicit_help_is_a_positive_cause_but_pause_alone_is_not(self):
        engine = self.engine(); state = self.seeded(engine)
        self.assertFalse(any(p["kind"] == "explicit-help" for p in state["proposals"]))
        help_event = copy.deepcopy(EVENTS[3]); help_event.update({"event_id": "explicit-help", "event_type": "task.help_requested", "sequence": 3, "source_timestamp": "2026-09-06T20:00:07+00:00", "received_timestamp": "2026-09-06T20:00:07+00:00"})
        changed = engine.ingest_event(help_event, CONTEXT, None)["state"]
        self.assertTrue(any(p["kind"] == "explicit-help" for p in changed["proposals"]))
        second = copy.deepcopy(help_event); second.update({"event_id": "explicit-help-2", "sequence": 4, "source_timestamp": "2026-09-06T20:00:08+00:00", "received_timestamp": "2026-09-06T20:00:08+00:00"})
        with_second = engine.ingest_event(second, CONTEXT, None)["state"]
        self.assertEqual(sum(p["kind"] == "explicit-help" and p["state"] == "proposed" for p in with_second["proposals"]), 2)

    def test_each_fact_expires_independently_while_participant_has_recent_noise(self):
        engine = self.engine(); self.seeded(engine)
        recent = copy.deepcopy(EVENTS[5]); recent.update({"event_id": "recent-pointer", "sequence": 6, "source_timestamp": "2026-09-06T20:00:09+00:00", "received_timestamp": "2026-09-06T20:00:09+00:00"})
        engine.ingest_event(recent, CONTEXT, None)
        self.now[0] = 1788724811000
        state = engine.snapshot("pupila-demo")
        self.assertIn("participant-a", state["replay"]["temporal"]["activeParticipants"])
        db = sqlite3.connect(engine.db_path)
        try:
            old_expiry = db.execute("SELECT expires_at FROM event_expirations WHERE event_id='evt-a-focus'").fetchone()[0]
            recent_expiry = db.execute("SELECT expires_at FROM event_expirations WHERE event_id='recent-pointer'").fetchone()[0]
        finally:
            db.close()
        self.assertLessEqual(old_expiry, self.now[0])
        self.assertGreater(recent_expiry, self.now[0])

    def test_future_event_is_durable_but_not_presence_and_decision_rechecks_expiry(self):
        engine = self.engine(); before = self.seeded(engine); proposal = next(p for p in before["proposals"] if p["state"] == "proposed")
        future = copy.deepcopy(EVENTS[0]); future.update({"event_id": "future", "sequence": 6, "source_timestamp": "2026-09-06T20:00:30+00:00", "received_timestamp": "2026-09-06T20:00:09+00:00"})
        accepted = engine.ingest_event(future, CONTEXT, None)
        self.assertEqual(accepted["status"], "accepted")
        self.assertNotIn("participant-a", engine.snapshot("pupila-demo")["replay"]["temporal"]["activeParticipants"])
        self.now[0] = 1788724830000
        with self.assertRaises(EngineError):
            engine.decide("pupila-demo", proposal["proposalId"], proposal["version"], "accept", "late-accept")

    def test_future_fact_activates_at_boundary_and_reference_matches_production(self):
        engine = self.engine(); self.seeded(engine)
        future = copy.deepcopy(EVENTS[0]); future.update({"event_id": "future-active", "sequence": 6, "source_timestamp": "2026-09-06T20:00:30+00:00", "received_timestamp": "2026-09-06T20:00:10+00:00"})
        engine.ingest_event(future, CONTEXT, None)
        self.now[0] = 1788724830000
        state = engine.tick("pupila-demo")
        self.assertIn("participant-a", state["replay"]["temporal"]["activeParticipants"])
        db = sqlite3.connect(engine.db_path)
        try:
            events = [json.loads(row[0]) for row in db.execute("SELECT event_json FROM events WHERE session_id='pupila-demo' AND accepted=1 ORDER BY arrival")]
            consent = {row[0]: (bool(row[1]), int(row[2])) for row in db.execute("SELECT participant_ref,consent,epoch_start FROM participants WHERE session_id='pupila-demo'")}
        finally:
            db.close()
        reference = evaluate_temporal_reference(events, consent, CONTEXT, self.now[0], 10_000)
        self.assertEqual(reference["acceptedEventIds"], [event["event_id"] for event in reference["eligibleEvents"]])
        oracle = CanonicalEventReplay().run(reference["eligibleEvents"], CONTEXT, consent=True)
        self.assertEqual(state["replay"]["acceptedCount"], oracle["acceptedCount"])
        self.assertEqual(state["replay"]["finalPupilaView"], oracle["finalPupilaView"])

    def test_help_uses_durable_evaluation_instant_after_clock_rewind(self):
        engine = self.engine(); self.seeded(engine)
        help_event = copy.deepcopy(EVENTS[3]); help_event.update({"event_id": "rewind-help", "event_type": "task.help_requested", "sequence": 3, "source_timestamp": "2026-09-06T20:00:07+00:00", "received_timestamp": "2026-09-06T20:00:07+00:00"})
        engine.ingest_event(help_event, CONTEXT, None)
        self.now[0] = 1788724830000
        engine.tick("pupila-demo")
        restarted = PupilaEngine(engine.db_path, clock=lambda: 1788724810000, stale_after_ms=10_000)
        state = restarted.tick("pupila-demo")
        self.assertFalse(any(p["kind"] == "explicit-help" and p["state"] == "proposed" for p in state["proposals"]))

    def test_future_help_is_inactive_until_its_exact_event_time(self):
        engine = self.engine(); self.seeded(engine)
        future_help = copy.deepcopy(EVENTS[3]); future_help.update({"event_id": "future-help", "event_type": "task.help_requested", "sequence": 3, "source_timestamp": "2026-09-06T20:00:30+00:00", "received_timestamp": "2026-09-06T20:00:10+00:00"})
        before = engine.ingest_event(future_help, CONTEXT, None)["state"]
        self.assertFalse(any(p["kind"] == "explicit-help" and p["state"] == "proposed" for p in before["proposals"]))
        self.now[0] = 1788724830000
        at_boundary = engine.tick("pupila-demo")
        self.assertTrue(any(p["kind"] == "explicit-help" and p["state"] == "proposed" for p in at_boundary["proposals"]))

    def test_tick_accepts_explicit_evaluation_instant(self):
        engine = self.engine(); fresh = self.seeded(engine)
        evaluated = engine.tick("pupila-demo", evaluation_ms=1788724830000)
        self.assertEqual(evaluated["replay"]["temporal"]["nowMs"], 1788724830000)
        self.assertEqual(evaluated["revision"], fresh["revision"] + 1)
        with self.assertRaises(EngineError):
            engine.tick("pupila-demo", evaluation_ms=True)

    def test_unchanged_consent_command_publishes_due_temporal_invalidation(self):
        engine = self.engine(); fresh = self.seeded(engine)
        self.now[0] = 1788724830000
        unchanged = engine.set_consent("pupila-demo", "participant-a", True)
        self.assertEqual(unchanged["status"], "unchanged")
        self.assertEqual(unchanged["state"]["pupila"]["proposalCount"], 0)
        self.assertEqual(unchanged["revision"], fresh["revision"] + 1)

    def test_snapshot_at_explicit_time_is_pure_and_does_not_commit_clock(self):
        engine = self.engine(); fresh = self.seeded(engine)
        preview = engine.snapshot("pupila-demo", evaluation_ms=1788724830000)
        self.assertEqual(preview["pupila"]["proposalCount"], 0)
        self.assertEqual(preview["revision"], fresh["revision"])
        current = engine.snapshot("pupila-demo")
        self.assertEqual(current["revision"], fresh["revision"])
        self.assertEqual(current["pupila"]["proposalCount"], 1)


if __name__ == "__main__":
    unittest.main()
