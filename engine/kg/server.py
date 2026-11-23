"""Stdlib-only JSON API around the Governance Gateway.

Runs on the QwenWork Agent Computer VM with ZERO pip installs; the Pages
console and the worker-agent interceptor call these endpoints.

  POST /intercept     {draft_id, action, text, payload_ids, recipient_emails}
  POST /owner_action  {id, approve: true|false}      # 1-click queued decision
  GET  /log           last 50 interceptions
  GET  /digest        morning-coffee briefing numbers
  GET  /health        ontology completeness probe (policy_cells == expected)
"""
from __future__ import annotations
import json, sqlite3, sys, datetime, threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).parent))
from engine import build_gateway, Gateway

DB = Path(__file__).parent / "kg.db"


def open_db() -> sqlite3.Connection:
    if DB.exists():
        conn = sqlite3.connect(DB, check_same_thread=False)
        try:
            conn.execute("SELECT 1 FROM interception_log")
            try:
                conn.execute("SELECT owner_status FROM interception_log")
            except sqlite3.OperationalError:      # pre-v2 db: add the column
                conn.execute("ALTER TABLE interception_log ADD COLUMN owner_status TEXT")
                conn.commit()
            return conn
        except sqlite3.OperationalError:
            conn.close()
            DB.unlink()
    return build_gateway(str(DB))


conn = open_db()
gw = Gateway(conn)
_LOCK = threading.Lock()  # serialized db/gateway access; verdicts are pure anyway


class H(BaseHTTPRequestHandler):
    def _json(self, obj, code: int = 200):
        body = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            req = json.loads(self.rfile.read(n))
        except json.JSONDecodeError:
            return self._json({"error": "bad json"}, 400)
        with _LOCK:
            if self.path == "/intercept":
                v = gw.evaluate(req["draft_id"], req["action"], req["text"],
                                req.get("payload_ids", []),
                                req.get("recipient_emails", []))
                return self._json(v)
            if self.path == "/owner_action":
                stamp = datetime.datetime.now().isoformat(timespec="seconds")
                cur = conn.execute(
                    "UPDATE interception_log SET owner_status = ? WHERE id = ?",
                    (f"{'approved' if req.get('approve') else 'rejected'}:{stamp}",
                     req["id"]))
                conn.commit()
                if cur.rowcount == 0:
                    return self._json({"error": "no such log id"}, 404)
                status = conn.execute("SELECT owner_status FROM interception_log "
                                      "WHERE id = ?", (req["id"],)).fetchone()[0]
                return self._json({"ok": True, "id": req["id"], "owner_status": status})
        return self._json({"error": "unknown path"}, 404)

    def do_GET(self):
        with _LOCK:
            if self.path.startswith("/health"):  # ontology completeness probe
                t = conn.execute("SELECT COUNT(*) FROM sensitivity_tier").fetchone()[0]
                a = conn.execute("SELECT COUNT(*) FROM action_class").fetchone()[0]
                return self._json({
                    "tiers": t, "actions": a,
                    "policy_cells": conn.execute(
                        "SELECT COUNT(*) FROM policy_rule").fetchone()[0],
                    "expected_cells": t * a,
                    "complete": conn.execute(
                        "SELECT COUNT(*) FROM policy_rule").fetchone()[0] == t * a,
                    "graph_nodes": conn.execute("SELECT COUNT(*) FROM node").fetchone()[0],
                    "graph_edges": conn.execute("SELECT COUNT(*) FROM edge").fetchone()[0],
                    "grounded_facts": conn.execute("SELECT COUNT(*) FROM fact").fetchone()[0]})
            if self.path.startswith("/digest"):
                return self._json(gw.digest())
            if self.path.startswith("/log"):
                rows = conn.execute("SELECT * FROM interception_log "
                                    "ORDER BY id DESC LIMIT 50").fetchall()
                cols = [d.name for d in conn.execute(
                    "SELECT * FROM interception_log LIMIT 1").description]
                return self._json([dict(zip(cols, r)) for r in rows])
        return self._json({"error": "unknown path"}, 404)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("Glass-Box gateway listening on :3000 (JSON, stdlib-only)")
    ThreadingHTTPServer(("0.0.0.0", 3000), H).serve_forever()
