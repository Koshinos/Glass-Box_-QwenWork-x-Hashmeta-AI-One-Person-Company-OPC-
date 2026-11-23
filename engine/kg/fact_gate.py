"""Fact Gate: deterministic numeric/UEN extraction checked against the KG.

Every money figure, percentage, and UEN in a draft is matched to a ground-truth
node. Mismatch => CONTRADICTION card with the exact contradicting source record.
Pure regex + SQL. Same draft text => same card list, byte-for-byte.
"""
from __future__ import annotations
import re

TOL_REL = 0.005  # 0.5% rounding tolerance; anything larger is a contradiction.

MONEY = re.compile(r"(?:S\$|SGD)\s?([\d,]+(?:\.\d+)?)\s?(million|mil|bn|billion|k|thousand)?", re.I)
PCT   = re.compile(r"([\d]+(?:\.\d+)?)\s*%")
UEN_RE = re.compile(r"\b(\d{8}[A-Z]|[STFG]\d{2}[A-Z]{1,2}\d{4}[A-Z])\b")
MULT = {None: 1, "k": 1e3, "thousand": 1e3, "mil": 1e6, "million": 1e6,
        "bn": 1e9, "billion": 1e9}
# Context keywords -> fact measure. Longest-keyword-first, first hit wins (deterministic).
MEASURE_KEYS = sorted(
    [("revenue", "revenue"), ("turnover", "revenue"),
     ("tender", "tender_award_value"), ("award", "tender_award_value"),
     ("invoice", "invoice_total"), ("billing", "invoice_total"),
     ("ppi", "benchmark_pct"), ("index", "benchmark_pct"),
     ("price inflation", "benchmark_pct"), ("benchmark", "benchmark_pct")],
    key=lambda x: (-len(x[0]), x[0]))
EXTERNAL_ACTIONS = {"external_email", "public_post", "third_party_upload"}


class FactGate:
    def __init__(self, g):
        self.g = g
        self.facts: dict[tuple[str, str], dict] = {}
        import json as _json
        self.uen_index = {}
        for nid, nd in g.nodes.items():
            uen = _json.loads(nd["props"]).get("uen")
            if uen:
                self.uen_index[uen] = nid

    def attach_facts(self, conn):
        self.facts = {}
        for e, m, v, u, p, s, a in conn.execute(
                "SELECT entity,measure,value,unit,period,source_uri,as_of_date FROM fact"):
            self.facts[(e, m)] = {"value": v, "unit": u, "period": p,
                                  "source_uri": s, "as_of_date": a}

    # ---- entity resolution: nearest fact-holding entity for this measure ----
    def _entity(self, text: str, up_to: int, measure: str | None,
                window: int = 90) -> str | None:
        uen = UEN_RE.search(text[max(0, up_to - window):up_to])
        if uen and uen.group(1) in self.uen_index:
            return self.uen_index[uen.group(1)]
        tl = re.sub(r"[^a-z0-9 ]", " ", text.lower())  # length-preserving sanitize
        best, best_pos = None, -1
        for nid in sorted(self.g.nodes):
            nd = self.g.nodes[nid]
            if nd["type"] not in ("client", "vendor", "tender", "record", "benchmark"):
                continue
            if measure and (nid, measure) not in self.facts:
                continue  # only entities whose facts we can actually check
            short = re.sub(r"\bPte\.?\s*Ltd\.?\b|\b& ?Co\b", " ", nd["name"], flags=re.I)
            key = re.sub(r"[^a-z0-9 ]", "", short.lower()).strip()[:16]
            if len(key) < 8:
                continue
            pos = tl.rfind(key, max(0, up_to - window), up_to)
            if pos > best_pos:
                best, best_pos = nid, pos
        return best

    def check_text(self, text: str) -> list[dict]:
        cards: list[dict] = []
        claims: list[tuple[int, float, str, str]] = []
        for m in MONEY.finditer(text):
            val = float(m.group(1).replace(",", "")) * (
                MULT[m.group(2).lower()] if m.group(2) else 1)
            claims.append((m.start(), val, "SGD", m.group(0)))
        for m in PCT.finditer(text):
            claims.append((m.start(), float(m.group(1)), "PCT", m.group(0)))
        claims.sort(key=lambda c: c[0])

        for pos, val, unit, snippet in claims:
            ctx = text[max(0, pos - 90):pos].lower()
            # Measure = the ground-truth keyword CLOSEST to the number
            # (ties broken by MEASURE_KEYS deterministic sort).
            measure, nearest = None, -1
            for kw, ms in MEASURE_KEYS:
                if kw in ctx:
                    i = ctx.rfind(kw)
                    if i > nearest:
                        nearest, measure = i, ms
            entity = self._entity(text, pos, measure)
            card = {"claim": snippet.strip(), "claim_value": val, "unit": unit,
                    "position": pos}
            if measure and entity and (entity, measure) in self.facts:
                f = self.facts[(entity, measure)]
                rel = abs(val - f["value"]) / max(abs(f["value"]), 1e-9)
                card.update(kg_value=f["value"], period=f["period"],
                            source_uri=f["source_uri"], as_of_date=f["as_of_date"],
                            matched_entity=entity, measure=measure,
                            verdict="VERIFIED" if rel <= TOL_REL else "FACT_CONTRADICTION")
            else:
                why = ("measure not inferable from context" if not measure else
                       "entity not resolvable" if not entity else
                       "no ground-truth fact for (entity, measure)")
                card.update(verdict="UNVERIFIED", reason=why)
            cards.append(card)

        for m in UEN_RE.finditer(text):
            ver = "VERIFIED" if m.group(1) in self.uen_index else "UNKNOWN_UEN"
            cards.append({"claim": m.group(1), "verdict": ver, "position": m.start(),
                          "type": "uen"})
        cards.sort(key=lambda c: (c["position"], c["claim"]))
        return cards

    def must_escalate(self, cards: list[dict], action: str) -> dict | None:
        """Deterministic uplift: a contradicted number sent externally is
        at minimum a REQUIRE_OWNER event, regardless of tier matrix."""
        if action not in EXTERNAL_ACTIONS:
            return None
        bad = [c for c in cards if c["verdict"] in ("FACT_CONTRADICTION", "UNKNOWN_UEN")]
        if not bad:
            return None
        return {"decision": "REQUIRE_OWNER",
                "rule_path": [f"Fact Gate uplift: {len(bad)} contradicted claim(s) in a "
                              f"{action} payload => REQUIRE_OWNER (never below policy matrix)"]}
