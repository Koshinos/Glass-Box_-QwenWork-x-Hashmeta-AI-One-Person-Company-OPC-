"""Governance Gateway core: composes Policy Gate + Fact Gate, logs every verdict.

final_decision = max(policy_decision, fact_uplift)   # never below the matrix
Deterministic end to end: identical inputs replay to identical verdicts.
"""
from __future__ import annotations
import json, sqlite3, datetime, pathlib

from policy_gate import Graph, DECISION_RANK, check_action as policy_check
from fact_gate import FactGate

HERE = pathlib.Path(__file__).parent


def build_gateway(db_path: str = ":memory:") -> sqlite3.Connection:
    # check_same_thread=False so the stdlib threaded HTTP server can share one conn;
    # all access is serialized by a lock at the HTTP layer.
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL") if db_path != ":memory:" else None
    conn.executescript((HERE / "schema.sql").read_text())
    conn.executescript((HERE / "seed.sql").read_text())
    real = HERE.parent.parent / "agent-computer" / "db_realdata.sql"
    if real.exists():          # same real GeBIZ layer, mapped to this schema
        kg = sqlite3.connect(":memory:")
        kg.executescript((HERE.parent.parent / "agent-computer" / "db_init.sql").read_text())
        kg.executescript(real.read_text())
        for nid, name, ntype, props in kg.execute(
                "SELECT id,name,type,props FROM kg_nodes WHERE type IN ('supplier','tender')"):
            p = json.loads(props)
            f = p.get("facts", {}).get("tender_award_value")
            conn.execute("INSERT OR REPLACE INTO node VALUES (?,?,?,?,'{}')",
                         (nid, name, ntype, "public"))
            if f:
                conn.execute("INSERT OR REPLACE INTO fact VALUES (?,?,?,?,?,?,?)",
                             (nid, "tender_award_value", float(f), "SGD",
                              p.get("as_of_date", ""), p.get("source_uri", ""),
                              p.get("as_of_date", "")))
            elif ntype == "tender":
                conn.execute("INSERT OR REPLACE INTO fact VALUES (?,?,?,?,?,?,?)",
                             ("sup:" + p["agency"].split()[0].lower(), "tender_award_value",
                              float(p["amount"]), "SGD", p["tender_no"], p["source_uri"],
                              p["as_of_date"]))
    return conn


class Gateway:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.graph = Graph(conn)
        self.facts = FactGate(self.graph)
        self.facts.attach_facts(conn)

    def evaluate(self, draft_id: str, action: str, text: str,
                 payload_ids: list[str], recipient_emails: list[str]) -> dict:
        policy = policy_check(self.graph, action, payload_ids, recipient_emails)
        cards = self.facts.check_text(text)
        uplift = self.facts.must_escalate(cards, action)
        decision = policy["decision"]
        paths = list(policy["rule_path"])
        if uplift and DECISION_RANK[uplift["decision"]] > DECISION_RANK[decision]:
            decision = uplift["decision"]
            paths += uplift["rule_path"]
        flagged = [c for c in cards
                   if c["verdict"] in ("FACT_CONTRADICTION", "UNKNOWN_UEN")]
        verdict = {"draft_id": draft_id, "action": action, "decision": decision,
                   "tier": policy["tier"], "rule_path": paths,
                   "facts_checked": len(cards), "facts_flagged": len(flagged),
                   "evidence_cards": cards}
        self.conn.execute(
            "INSERT INTO interception_log(ts,draft_id,action_key,decision,rule_path,"
            "facts_checked,facts_flagged,evidence) VALUES(?,?,?,?,?,?,?,?)",
            (datetime.datetime.now().isoformat(timespec="seconds"), draft_id, action,
             decision, " || ".join(paths), len(cards), len(flagged),
             json.dumps(cards)))
        self.conn.commit()
        return verdict

    def digest(self, window_hours: int = 24) -> dict:
        """Morning-coffee briefing: pure SQL aggregation, no generation."""
        since = (datetime.datetime.now() - datetime.timedelta(hours=window_hours)
                 ).isoformat(timespec="seconds")
        rows = self.conn.execute(
            "SELECT decision, COUNT(*), SUM(facts_flagged) FROM interception_log "
            "WHERE ts >= ? GROUP BY decision", (since,)).fetchall()
        d = dict((r[0], (r[1], r[2])) for r in rows)
        blocked = d.get("HARD_BLOCK", (0, 0))[0]
        pending = d.get("REQUIRE_OWNER", (0, 0))[0]
        corrected = sum(v[1] for v in d.values())
        passed = d.get("ALLOW", (0, 0))[0]
        return {"blocked": blocked, "awaiting_owner": pending,
                "facts_corrected": corrected, "auto_allowed": passed,
                "generated_at": datetime.datetime.now().isoformat(timespec="seconds")}
