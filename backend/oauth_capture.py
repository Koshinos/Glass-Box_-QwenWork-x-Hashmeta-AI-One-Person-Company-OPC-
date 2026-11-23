"""oauth_capture.py — completes the Hashmeta OAuth 2.1 (PKCE) dance for the gateway.

Run modes:
  serve            listen on http://localhost:8199/callback; exchange code
                   automatically when the consent redirect lands (use with an
                   in-sandbox browser).
  finish "<url>"   paste the final redirect URL (or a bare ?code= value) after
                   approving in any browser, even if the page failed to load.

Tokens are stored at ~/.glassbox/hashmeta_token.json (mode 0600). Never printed.
"""
from __future__ import annotations
import json, os, sys, time, urllib.parse, urllib.request, base64, hashlib, secrets

import pathlib as _pl
HOME = str(_pl.Path(__file__).resolve().parent / ".glassbox")  # workspace-persistent, not sandbox-home
FLOW = HOME + "/hashmeta_flow.json"
TOKEN = HOME + "/hashmeta_token.json"
UA = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/130.0 Safari/537.36",
      "content-type": "application/x-www-form-urlencoded", "accept": "application/json"}


def exchange(code: str) -> dict:
    flow = json.load(open(FLOW))
    if not code:
        raise SystemExit("no code supplied")
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": flow["redirect_uri"], "client_id": flow["client"]["client_id"],
        "code_verifier": flow["verifier"]}).encode()
    req = urllib.request.Request("https://app.hashmeta.ai/api/mcp-oauth/token",
                                 data=data, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=25))
    if "access_token" not in d:
        raise SystemExit("token exchange failed: no access_token in response")
    tok = {"access_token": d["access_token"], "refresh_token": d.get("refresh_token"),
           "expires_at": time.time() + d.get("expires_in", 3600),
           "client_id": flow["client"]["client_id"],
           "token_endpoint": "https://app.hashmeta.ai/api/mcp-oauth/token"}
    with open(TOKEN, "w") as f:
        json.dump(tok, f)
    os.chmod(TOKEN, 0o600)
    print("token stored; expires_in", d.get("expires_in"))
    return tok


def serve():
    from http.server import BaseHTTPRequestHandler, HTTPServer

    flow = json.load(open(FLOW))
    done = {"ran": False}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if q.get("state", [""])[0] != flow["state"]:
                self.send_response(400); self.end_headers()
                self.wfile.write(b"state mismatch - restart the consent link")
                return
            if "code" in q:
                exchange(q["code"][0])
                done["ran"] = True
                self.send_response(200)
                self.send_header("content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    ("<body style='font:16px system-ui;background:#0a0f16;"
                     "color:#e9eff7;display:grid;place-items:center;height:100vh'>"
                     "<div>\u2713 Hashmeta connected \u2014 return to Glass-Box.</div>"
                     "</body>").encode())
            else:
                self.send_response(400); self.end_headers()
                self.wfile.write((q.get("error", ["no code"])[0]).encode())

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 8199), H)
    print("listening on localhost:8199/callback …")
    while not done["ran"] and time.time() < (start := time.time()) + 600:
        srv.handle_request()
    print("capture window closed")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "finish":
        raw = sys.argv[2]
        code = raw if "?" not in raw else urllib.parse.parse_qs(
            urllib.parse.urlparse(raw).query).get("code", [""])[0]
        exchange(code)
    else:
        serve()
