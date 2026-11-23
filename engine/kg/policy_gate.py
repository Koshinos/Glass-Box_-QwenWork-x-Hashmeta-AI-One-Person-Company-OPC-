"""Policy Gate: deterministic graph traversal over the sensitivity ontology.

NO LLM calls. No randomness. No tuned vibes.
Verdict is a pure function of (action, payload subgraph, recipient rows).
Fail-closed everywhere: missing matrix cell raises; unknown recipient escalates.
"""
from __future__ import annotations

# Deterministic decision ordering: max() picks the most restrictive verdict.
DECISION_RANK = {"ALLOW": 0, "REQUIRE_OWNER": 1, "HARD_BLOCK": 2}
TIER_OF_RANK = {0: "public", 1: "internal", 2: "client_confidential", 3: "regulated"}
INHERIT_RELS = ("references", "contains", "derived_from")
HOP_CAP = 6  # ontology depth is <4 everywhere; cap only guards against crafted cycles


class Graph:
    def __init__(self, conn):
        self.tier_rank = dict(conn.execute(
            "SELECT key, rank FROM sensitivity_tier").fetchall())
        self.matrix = {(t, a): (d, r) for t, a, d, r in conn.execute(
            "SELECT tier_key, action_key, decision, rule_text FROM policy_rule")}
        self.nodes = {row[0]: {"name": row[1], "type": row[2], "tier": row[3],
                               "props": row[4]}
                      for row in conn.execute(
            "SELECT id, name, type, tier, props FROM node").fetchall()}
        self.out: dict[str, list[tuple[str, str]]] = {}
        self.parents: dict[str, list[str]] = {}
        for s, rel, d in conn.execute("SELECT src, rel, dst FROM edge"):
            self.out.setdefault(s, []).append((rel, d))
            self.parents.setdefault(d, []).append(s)
        self.recipients = {e: (n, c, o) for n, e, c, o in conn.execute(
            "SELECT node_id,email,tier_ceiling,owner_client_id FROM recipient")}

    def rank_of(self, node_id: str) -> int:
        t = self.nodes[node_id]["tier"]
        return self.tier_rank[t] if t else 0

    def closure(self, node_id: str) -> list[str]:
        """BFS over inheritance edges. Sorted expansion => order is reproducible."""
        seen, frontier, order, hops = {node_id}, [node_id], [node_id], 0
        while frontier and hops < HOP_CAP:
            nxt = []
            for s in sorted(frontier):
                for rel, d in sorted(self.out.get(s, [])):
                    if rel in INHERIT_RELS and d not in seen:
                        seen.add(d); nxt.append(d); order.append(d)
            frontier, hops = sorted(nxt), hops + 1
        return order

    def sensitive_records(self, payload_ids: list[str]) -> tuple[int, list[str], list[str]]:
        """Returns (effective rank, max-ranked nodes, client-confidential-or-higher nodes)."""
        nodes = sorted({n for p in payload_ids for n in self.closure(p)})
        rank = max(self.rank_of(n) for n in nodes) if nodes else 0
        top = [n for n in nodes if self.rank_of(n) == rank]
        risky = [n for n in nodes if self.rank_of(n) >= 2]
        return rank, top or payload_ids, risky

    def owner_client_of(self, rec_id: str) -> str | None:
        for s in sorted(self.parents.get(rec_id, [])):
            if any(rel == "contains" for rel, d in self.out[s] if d == rec_id):
                return s
        return None

    def matrix_cell(self, tier_key: str, action_key: str):
        cell = self.matrix.get((tier_key, action_key))
        if cell is None:  # fail-closed: ontology must be exhaustive
            raise KeyError(f"POLICY GAP: no rule for ({tier_key},{action_key}); request aborted")
        return cell


def check_action(g: Graph, action: str, payload_ids: list[str],
                 recipient_emails: list[str]) -> dict:
    """Return the Policy Gate verdict: {decision, rule_path, tier, rank}."""
    rank, top, risky = g.sensitive_records(payload_ids)
    tier_key = TIER_OF_RANK[rank]
    decision, rule_text = g.matrix_cell(tier_key, action)
    paths = [f"{'; '.join(top)} [closure rank={rank}, {len(risky)} risky node(s)]"
             f" x {action} => {decision} | {rule_text}"]

    # Authorized-Recipient Exception: ONLY for external_email of confidential
    # payloads whose matrix cell is REQUIRE_OWNER. Regulated has no exception cell.
    if action == "external_email" and decision == "REQUIRE_OWNER" and rank == 2:
        ok = True
        for email in sorted(set(recipient_emails)):
            row = g.recipients.get(email)
            if row is None:
                ok = False
                paths.append(f"recipient({email}) absent from authorization table => "
                             "ceiling=-1 (fail-closed) => HARD_BLOCK")
                continue
            _, ceiling, owner = row
            if ceiling < rank:
                ok = False
                paths.append(f"recipient({email}) ceiling={ceiling} < payload rank={rank}"
                             " => HARD_BLOCK")
            wrong = [r for r in risky if owner != g.owner_client_of(r)]
            if wrong:
                ok = False
                paths.append(f"recipient({email}) owner={owner} != client_of({'; '.join(wrong)})"
                             " => cross-client disclosure => HARD_BLOCK")
        if ok:
            decision = "ALLOW"
            paths.append("Authorized-Recipient Exception satisfied for every recipient "
                         "and every risky record => REQUIRE_OWNER -> ALLOW")
        else:
            decision = "HARD_BLOCK"  # any failed ceiling/owner/known-party test

    return {"decision": decision, "rule_path": paths, "tier": tier_key, "rank": rank}
