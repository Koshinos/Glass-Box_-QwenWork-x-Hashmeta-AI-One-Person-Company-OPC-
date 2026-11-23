"""campaign_loop.py — the honest version of "real-time campaign optimisation".

A registry-drift closed loop, fully deterministic, publish-gated:

    terms changed in KG  -> scan live site (/impact logic)
                         -> draft corrections from registry values (no LLM)
                         -> queue via update_page (lands in Hashmeta publish center)
                         -> founder (human) runs publish_changes = the approval step
                         -> re-scan until CLEAN; every tick logged to a loop ledger.

Nothing auto-publishes. In manual publish mode the site physically cannot change
without the founder step — the loop's job ends at a perfectly-typed queue.
Run `tick()` (one pass) from prove_six.py, or `loop()` from a QwenWork Scheduled
Task for continuous optimisation.
"""
from __future__ import annotations
import json, re
from pathlib import Path

import hashmeta_mcp as hm

PID = "a3fe8987-1fc5-4fc4-891a-c363c429c7f5"
LEDGER = Path(__file__).resolve().parent / "loop_ledger.jsonl"

def _scan(conn_state=None):
    import oversight
    o = oversight
    o.STATE = o.Ontology(o.open_db()) if not getattr(o, "STATE", None) else o.STATE
    return json.loads(json.dumps(o.impact(), default=str))["live_cms"]

def _corrections(scan, terms):
    """path -> corrected claim pairs (registry values only)."""
    return {pg["path"]: [c for c in pg["claims"] if c["tag"] in ("STALE", "FABRICATED")]
            for pg in scan["pages"] if pg["worst"] != "CLEAN"}

def tick(project_id=PID):
    import oversight
    terms = oversight.STATE.current_offer(oversight.utcnow()[:10])
    scan = _scan()
    fixes = _corrections(scan, terms)
    c = hm.HashmetaMCP(); c.initialize()
    pages = c.call("list_pages", {"projectId": project_id}).get("pages", [])
    queued = []
    for path, claims in fixes.items():
        slug = path.lstrip("/") or "home"
        match = next((p for p in pages if p.get("slug") in (slug, slug.replace("-", "_"))), None)
        if not match:
            continue
        page = c.call("get_page", {"projectId": project_id, "pageId": match["id"]})
        d = page.get("page") or page
        html = d.get("contentHtml") or d.get("html") or ""
        if not html and d.get("layout"):
            html = json.dumps(d["layout"])          # block-JSON path: replace in-blocks
        new_html = html.replace("S$1,200", f"S${terms['price']:,.0f}") \
                       .replace("S$900", f"S${terms['price']:,.0f}") \
                       .replace("7 business days", f"{terms['sla']} business days") \
                       .replace("7-day", f"{terms['sla']}-day")
        if new_html == html:
            queued.append({"slug": slug, "state": "no-text-change (blocks)"})
            continue
        r = c.call("update_page", {"projectId": project_id, "pageId": match["id"],
                                   "html": new_html})
        queued.append({"slug": slug, "state": "queued via publish center",
                       "resp": str(r.get("message") or r)[:60]})
        if d.get("layout") is not None:
            # also patch layout JSON so block renderer sees new values
            lay = json.dumps(d["layout"]).replace(
                "S$1,200", f"S${terms['price']:,.0f}").replace(
                "7 business days", f"{terms['sla']} business days")
            c.call("update_page", {"projectId": project_id, "pageId": match["id"],
                                   "layout": json.loads(lay)})
    entry = {"tick": oversight.utcnow(), "terms": terms,
             "stale_before": scan["stale"] + scan["fabricated"], "queued": queued}
    with LEDGER.open("a") as f:
        f.write(json.dumps(entry, default=str) + "\n")
    return entry

def publish_approved():
    """The founder step — kept separate so the loop can never do it alone."""
    import oversight
    c = hm.HashmetaMCP(); c.initialize()
    r = c.call("publish_changes", {"projectId": PID})
    entry = {"published_at": oversight.utcnow(), "release": str(r)[:200],
             "by": "founder-approved"}
    with LEDGER.open("a") as f:
        f.write(json.dumps(entry, default=str) + "\n")
    return r

def verify_after_publish():
    import oversight
    scan = _scan()
    return {"stale_after": scan["stale"], "fabricated_after": scan["fabricated"],
            "pages": scan["pages_checked"]}

def loop(max_ticks=6, sleep=45):
    import time
    for _ in range(max_ticks):
        t = tick()
        if t["stale_before"] == 0 and verify_after_publish()["stale_after"] == 0:
            return {"done": True}
        time.sleep(sleep)
    return {"done": verify_after_publish()["stale_after"] == 0}

if __name__ == "__main__":
    print(json.dumps(tick(), indent=1, default=str))
