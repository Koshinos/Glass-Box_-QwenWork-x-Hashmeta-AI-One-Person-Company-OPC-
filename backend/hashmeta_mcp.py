"""hashmeta_mcp.py — minimal MCP-over-HTTP client for the Hashmeta connector.

Auth model (both supported, token read from ~/.glassbox/hashmeta_token.json):
  1) API token  -> {"bearer": "<token you created in the Hashmeta dashboard>"}
  2) OAuth 2.1  -> {"access_token": "...", "refresh_token": "...",
                    "client_id": "...", "token_endpoint": "..."}  (from oauth_capture.py)

MCP transport: JSON-RPC 2.0 POST to https://app.hashmeta.ai/api/mcp with
  Authorization: Bearer <token>, and (optional) Mcp-Session-Id header from initialize.

This module only *uses* the connector; it never prints tokens/secrets.
"""
from __future__ import annotations
import json, os, urllib.request, urllib.parse

MCP_URL = "https://app.hashmeta.ai/api/mcp"
import pathlib as _pl
HOME = str(_pl.Path(__file__).resolve().parent / ".glassbox")  # workspace-persistent, not sandbox-home
TOKEN_PATH = os.path.join(HOME, "hashmeta_token.json")
_CLIENT_HEADER = {"user-agent":
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/130.0 Safari/537.36"}


def _bearer() -> str | None:
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        d = json.load(open(TOKEN_PATH))
    except (json.JSONDecodeError, OSError):
        return None
    return d.get("bearer") or d.get("access_token")


class McpError(RuntimeError):
    pass


class HashmetaMCP:
    def __init__(self, bearer: str | None = None):
        self.bearer = bearer or _bearer()
        self.session_id: str | None = None
        self._id = 0

    @property
    def authenticated(self) -> bool:
        return bool(self.bearer)

    def _post(self, payload: dict, extra_headers: dict | None = None) -> dict:
        if not self.bearer:
            raise McpError("no Hashmeta token — run oauth_capture.py or set an API token")
        headers = {"content-type": "application/json",
                   "accept": "application/json, text/event-stream",
                   "authorization": f"Bearer {self.bearer}",
                   "mcp-protocol-version": "2025-03-26", **_CLIENT_HEADER}
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        if extra_headers:
            headers.update(extra_headers)
        req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode(),
                                     headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            sid = r.headers.get("mcp-session-id")
            if sid:
                self.session_id = sid
            body = r.read().decode()
            # some servers reply as SSE (data: {...}); others plain JSON
            if body.startswith("event:") or "\ndata: " in body or body.startswith("data:"):
                for line in body.splitlines():
                    if line.startswith("data:"):
                        return json.loads(line[5:].strip())
                return {}
            return json.loads(body) if body else {}

    def rpc(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        out = self._post({"jsonrpc": "2.0", "id": self._id, "method": method,
                          "params": params or {}})
        if "error" in out:
            raise McpError(out["error"].get("message", "mcp error"))
        return out.get("result", {})

    def initialize(self) -> dict:
        res = self.rpc("initialize", {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "glassbox-gateway", "version": "2.0"}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return res

    def tools(self) -> list[dict]:
        return self.rpc("tools/list").get("tools", [])

    def call(self, name: str, args: dict):
        res = self.rpc("tools/call", {"name": name, "arguments": args})
        items = res.get("content", [])
        texts = [c.get("text") for c in items if c.get("type") == "text"]
        joined = "\n".join(t for t in texts if t)
        try:
            return json.loads(joined)
        except json.JSONDecodeError:
            return joined
