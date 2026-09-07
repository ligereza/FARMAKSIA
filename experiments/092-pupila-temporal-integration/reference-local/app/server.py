from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r"C:\IA\FARMAXIA\experiments\090-farmaxia-adaptive-representation-layer")
sys.path.insert(0, str(SOURCE))
try:
    from app.pupila_engine import EngineError, PupilaEngine
except ModuleNotFoundError:
    from pupila_engine import EngineError, PupilaEngine  # type: ignore

EVENTS = [
    {"event_id": "evt-a-focus", "schema_version": 1, "source_app": "local-replay", "event_type": "focus.changed", "channel": "focus", "payload": {"focused": True}, "source_timestamp": "2026-09-06T20:00:00+00:00", "received_timestamp": "2026-09-06T20:00:00+00:00", "session_id": "pupila-demo", "peer_id": "participant-a", "sequence": 1, "raw_hash": "fixture-a-focus", "provenance": {"kind": "synthetic", "label": "ensayo local"}},
    {"event_id": "evt-b-focus", "schema_version": 1, "source_app": "local-replay", "event_type": "focus.changed", "channel": "focus", "payload": {"focused": True}, "source_timestamp": "2026-09-06T20:00:01+00:00", "received_timestamp": "2026-09-06T20:00:01+00:00", "session_id": "pupila-demo", "peer_id": "participant-b", "sequence": 1, "raw_hash": "fixture-b-focus", "provenance": {"kind": "synthetic", "label": "ensayo local"}},
    {"event_id": "evt-a-pointer", "schema_version": 1, "source_app": "local-replay", "event_type": "pointer.moved", "channel": "pointer", "payload": {"x": 0.42, "y": 0.58}, "source_timestamp": "2026-09-06T20:00:02+00:00", "received_timestamp": "2026-09-06T20:00:02+00:00", "session_id": "pupila-demo", "peer_id": "participant-a", "sequence": 2, "raw_hash": "fixture-a-pointer", "provenance": {"kind": "synthetic", "label": "ensayo local"}},
    {"event_id": "evt-b-guide", "schema_version": 1, "source_app": "local-replay", "event_type": "task.paused", "channel": "task", "payload": {"progress": 0.4}, "source_timestamp": "2026-09-06T20:00:03+00:00", "received_timestamp": "2026-09-06T20:00:03+00:00", "session_id": "pupila-demo", "peer_id": "participant-b", "sequence": 2, "raw_hash": "fixture-b-guide", "provenance": {"kind": "synthetic", "label": "ensayo local"}},
    {"event_id": "evt-a-pointer-2", "schema_version": 1, "source_app": "local-replay", "event_type": "pointer.moved", "channel": "pointer", "payload": {"x": 0.48, "y": 0.56}, "source_timestamp": "2026-09-06T20:00:04+00:00", "received_timestamp": "2026-09-06T20:00:04+00:00", "session_id": "pupila-demo", "peer_id": "participant-a", "sequence": 3, "raw_hash": "fixture-a-pointer-2", "provenance": {"kind": "synthetic", "label": "ensayo local"}},
    {"event_id": "evt-a-pointer-3", "schema_version": 1, "source_app": "local-replay", "event_type": "pointer.moved", "channel": "pointer", "payload": {"x": 0.53, "y": 0.54}, "source_timestamp": "2026-09-06T20:00:05+00:00", "received_timestamp": "2026-09-06T20:00:05+00:00", "session_id": "pupila-demo", "peer_id": "participant-a", "sequence": 4, "raw_hash": "fixture-a-pointer-3", "provenance": {"kind": "synthetic", "label": "ensayo local"}},
    {"event_id": "evt-a-pointer-4", "schema_version": 1, "source_app": "local-replay", "event_type": "pointer.moved", "channel": "pointer", "payload": {"x": 0.58, "y": 0.51}, "source_timestamp": "2026-09-06T20:00:06+00:00", "received_timestamp": "2026-09-06T20:00:06+00:00", "session_id": "pupila-demo", "peer_id": "participant-a", "sequence": 5, "raw_hash": "fixture-a-pointer-4", "provenance": {"kind": "synthetic", "label": "ensayo local"}},
]
CONTEXT = {"sessionId": "pupila-demo", "roomId": "atelier-local", "surfaceId": "lamina-01", "host": "replay", "task": "preparar-lamina"}


def seed(engine: PupilaEngine):
    try:
        engine.snapshot("pupila-demo")
    except EngineError:
        engine.ingest_batch(EVENTS, CONTEXT, {"participant-a": True, "participant-b": True})


class Handler(BaseHTTPRequestHandler):
    engine: PupilaEngine

    def log_message(self, *_args):
        return

    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def body(self):
        size = int(self.headers.get("Content-Length", "0")); return json.loads(self.rfile.read(size) or b"{}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            session_id = parse_qs(parsed.query).get("sessionId", ["pupila-demo"])[0]
            raw_evaluation = parse_qs(parsed.query).get("evaluationMs", [None])[0]
            try: return self.send_json(self.engine.snapshot(session_id, int(raw_evaluation) if raw_evaluation is not None else None))
            except EngineError as exc: return self.send_json({"ok": False, "error": str(exc)}, 404)
        path = "/public/index.html" if parsed.path == "/" else parsed.path
        file_path = (ROOT / path.lstrip("/")).resolve()
        if ROOT not in file_path.parents or not file_path.is_file(): return self.send_error(404)
        content_type = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8"}.get(file_path.suffix, "application/octet-stream")
        raw = file_path.read_bytes(); self.send_response(200); self.send_header("Content-Type", content_type); self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def do_POST(self):
        try:
            data = self.body(); path = urlparse(self.path).path
            if path == "/api/events":
                out = self.engine.ingest_event(data["event"], data.get("context"), data.get("consent")); return self.send_json(out, 201 if out["status"] == "accepted" else 200)
            if path == "/api/events/batch": return self.send_json({"results": self.engine.ingest_batch(data["events"], data.get("context"), data.get("consentByParticipant", {}))}, 201)
            if path == "/api/consent": return self.send_json(self.engine.set_consent(data["sessionId"], data["participantRef"], data["consent"], data.get("context")))
            if path == "/api/tick": return self.send_json(self.engine.tick(data["sessionId"], data.get("evaluationMs")))
            if path == "/api/decision":
                out = self.engine.decide(data["sessionId"], data["proposalId"], int(data["proposalVersion"]), data["decision"], data["decisionId"], data.get("context"), data.get("revertDecisionId")); return self.send_json(out)
            return self.send_error(404)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, EngineError) as exc: return self.send_json({"ok": False, "error": str(exc)}, 400)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765; db = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "work" / "pupila-state.sqlite3"
    engine = PupilaEngine(db); seed(engine); Handler.engine = engine
    print(f"PUPILA/LUCIDA local en http://127.0.0.1:{port} (db={db})")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
