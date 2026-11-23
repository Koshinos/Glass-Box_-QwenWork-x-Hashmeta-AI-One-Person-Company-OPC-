# 3-Minute Demo — Shot Script (AvePoint Track 2)
**Order matches the required moments exactly. Total 3:00. Rehearse twice; the pack is deterministic, so takes never fail.**

---

### 0:00 – 0:30 · THE SETUP
**Screen:** terminal left (`curl -XPOST localhost:8000/simulate/rogue-pack` → 7/7 table), console right (`● LIVE` pill), `/health` one-liner visible.
> "This is Glass-Box: a one-person Singapore firm's AI worker, gated by a knowledge
> graph instead of another model. Seven scripted rogue behaviours — leaks, PII,
> fabricated awards, rogue payments, silent bulk exports, stale promises. Caught:
> seven. False positives on the legit controls: zero. And `llm_in_decision_path:
> false` is a field on the health endpoint, not a claim in my slides — rerun it,
> same bytes."

### 0:30 – 1:15 · RISKY ACTION CAUGHT & STOPPED
**Screen:** console Queue → click **Run rogue pack** if not fresh → open R1 row.
> "The agent drafts an email of the client's confidential NusaGov proposal — to a
> journalist. Watch the path: proposal, classified client-confidential,
> send_external_email. The matrix says founder sign-off; the recipient isn't in the
> authorization graph, so fail-closed pushes it to hard-block. The `/send` response
> literally says `executed: false` — the byte never left the building. R2's payroll
> export dies the same way: one graph hop to a PDPA node and every action is blocked
> by the wildcard rule."
*(Beat: show R2's card — NRIC string present in draft = regulated-PII flag.)*

### 1:15 – 2:00 · MADE-UP NUMBER FLAGGED WITH EVIDENCE
**Screen:** Fact-Check Diff panel → R3 card, then **R7 card** (the real one) — data.gov.sg link visible.
> "Twice on camera. First, an award that grew from S$412,000 to a claimed 1.2
> million — denied by the ground-truth node, receipts inline. Second is my favourite:
> the agent quotes a **true** number — CrimsonLogic's S$4.5M ACRA award — but the
> public GeBIZ register, pulled live from data.gov.sg with every tender row, says its
> latest award is S$987,850. A true-but-stale statement is still a false promise, and
> the gate holds it with the correct sentence pre-written beside it. Same doctrine
> covers the marketing pages themselves: this site's `/impact` scan caught a 'from
> S$900' intro price that exists in no version of our terms — fabricated, by the
> way, because we planted that lie to see if it would survive. It didn't."

### 2:00 – 2:40 · MORNING COFFEE BRIEFING
**Screen:** console Briefing card (4 big numbers + worst-catch quote). *Optional if the scheduled task exists by filming:* phone with the pushed digest.
> "And this is what governance feels like for a founder: fifteen seconds. Four
> actions blocked overnight, three fabricated or stale claims flagged, one draft
> that needs my actual judgement, three auto-released with every number verified —
> plus a note of every public page that contradicts current terms. It's pure SQL
> aggregation. The model drafted; the graph decided; I decide the rest."
*(Grandfathering closer, 10 s:)* "And the same S$1,200 that was HELD for a new
prospect — this Nexgate email — was PASSPORTED, because their signed 2025 agreement
predates the change. One number, two correct answers."

### 2:40 – 3:00 · LIVE URLS
**Screen:** console URL → site URL → `/registry-change-log` (graph-drafted live changelog, real award anchors on page) → pamphlet PDF flipped once.
> "The console: QwenWork Pages. The public source of truth it polices: Hashmeta.
> Even this pamphlet's price block is checked by the Promise Gate. Glass-Box —
> your AI worker, kept honest."

---

## Narration source notes (if judges ask)
- Digital economy S$144.1B / 18.6% GDP & SME AI 14.5→23.4%: IMDA 2025 releases (research §1).
- "17–34% wrong in hallucination-free legal AI": Stanford RegLab 2024 (full-text verified).
- Air Canada tribunal: liability precedent (BBC/ABA).
- GeBIZ/ACRA/SingStat dataset IDs + refresh dates: research §4 — all live-checked 22 Nov.
- All fictitious entities labelled in README & pamphlet fine print.

## If live network fails on take day
- Console boots in SAMPLE (archived real run, byte-identical engine): moments 1–4 all playable from screenshots in `submission/screenshots/` with the line: "same deterministic engine — here's its archived output plus the live replay once connectivity is back."
- Pack + real-data R7/B4 run **fully offline** (`db_realdata.sql` ships the verbatim rows).

## Cut list (extras if you find 15 seconds)
`/health` zoom (`llm_in_decision_path: 0`), the seal-strip stamps landing,
loop_ledger showing queue→flush timestamps, QR scan to the governed form.
