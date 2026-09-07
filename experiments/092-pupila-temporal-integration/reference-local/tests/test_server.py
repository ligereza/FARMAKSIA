import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from app.pupila_engine import PupilaEngine
from app.server import CONTEXT, EVENTS, Handler


class HttpContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.now = [1788724810000]
        self.engine = PupilaEngine(Path(self.tmp.name) / "http.sqlite3", clock=lambda: self.now[0], stale_after_ms=10_000)
        self.engine.ingest_batch(copy.deepcopy(EVENTS), CONTEXT, {"participant-a": True, "participant-b": True})
        Handler.engine = self.engine
        self.server = __import__("http.server", fromlist=["ThreadingHTTPServer"]).ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(timeout=2); self.tmp.cleanup()

    def request(self, path, method="GET", body=None):
        data = json.dumps(body).encode() if body is not None else None
        request = Request(self.base + path, data=data, method=method, headers={"Content-Type": "application/json"})
        with urlopen(request) as response:
            return json.loads(response.read())

    def test_state_evaluation_is_pure_over_http(self):
        preview = self.request("/api/state?sessionId=pupila-demo&evaluationMs=1788724830000")
        current = self.request("/api/state?sessionId=pupila-demo")
        self.assertEqual(preview["pupila"]["proposalCount"], 0)
        self.assertEqual(current["pupila"]["proposalCount"], 1)
        self.assertEqual(current["revision"], preview["revision"])

    def test_tick_over_http_publishes_temporal_transition(self):
        self.now[0] = 1788724830000
        ticked = self.request("/api/tick", "POST", {"sessionId": "pupila-demo"})
        self.assertEqual(ticked["pupila"]["proposalCount"], 0)
        self.assertEqual(ticked["revision"], 8)
        repeated = self.request("/api/tick", "POST", {"sessionId": "pupila-demo"})
        self.assertEqual(repeated["revision"], 8)


if __name__ == "__main__":
    unittest.main()
