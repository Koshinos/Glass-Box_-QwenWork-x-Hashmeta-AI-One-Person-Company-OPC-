# AGENTS.md — Glass-Box Founder AI Oversight Console

## Project background

A solo Singapore B2B/compliance consultancy (OPC) runs a QwenWork worker agent
for client research, tender drafting and outreach. Every risky side effect is
intercepted by a deterministic, graph-backed governance gateway running on the
founder's QwenWork Agent Computer VM (FastAPI + SQLite; endpoints:
`/health`, `/intercept`, `/audit`, `/audit/{id}/decide`, `/briefing/morning`,
`/simulate/rogue-pack`). This console is the founder's oversight surface,
built for the AvePoint Track 2 (AI Governance) hackathon submission (judging:
zero missed violations beats a clever dashboard).

Target users: the founder (15-second morning review, 1-click decisions) and
hackathon judges (prove deterministic 5/5 catch rate live).

## Product shape (v2 — Promise Gate merged)

- Static QW Page (Vite + React + TS). All logic runs in the browser; no
  Page-owned server, no durable shared records.
- The gateway URL is unknown at build time (`<YOUR_VM_URL>` placeholder), so
  the console resolves its API base at runtime: `?api=` query param →
  localStorage → else SAMPLE mode from embedded fixtures (v2 fixtures captured
  cold-run 2026-11-22; pack = R1–R6 plus controls B1–B3).
- Three deterministic gates behind every send: Policy (sensitivity tiers),
  Fact (ledger provenance), Promise (effective-dated offer terms). Same
  sentence — retainer S$1,200, 7-day delivery — is HELD for a new prospect
  (PROMISE_CONFLICT + corrected wording from current terms) and ALLOWED to
  the client whose signed MSA predates the change (vintage exemption).
- Four views, no clutter:
  1. Rogue-Pack Stress Bar — one button → `POST /simulate/rogue-pack`,
     live `6/6` "Violations Caught (0 Missed)" badge + per-scenario seal strip
     (R1–R6 expected non-ALLOW, B1–B3 benign controls expected ALLOW).
  2. Intercepted Actions Queue — HARD_BLOCK + REQUIRE_OWNER events with
     ontology breadcrumbs (`node → tier → action → verdict`) parsed from
     `rule_path`; Approve/Reject call `POST /audit/{id}/decide` (sample mode
     records locally and says so).
  3. Fact-Check Diff Panel — latest flagged claims: agent number (red) vs
     verified KG value or current-effective term (mint), with
     `source_uri`/`effective_date`, plus Promise-Gate correction line
     (`row.corrected`) rendered inside PROMISE_CONFLICT cards.
  4. Morning Coffee Briefing — `GET /briefing/morning` executive card:
     blocked overnight, fabricated stats flagged, items awaiting sign-off,
     worst catch.
- Design: dark ink-blue "audit instrument", brass engraved accents, Newsreader
  display + IBM Plex Sans/Mono; signature = ink-stamp seal strip that lands
  scenario-by-scenario after a pack run. Reduced motion respected.

## Scope boundaries / constraints

- Fixtures are captured verbatim from a fresh local gateway cold run (2026-11-20)
  with the rogue pack executed; they are presentation fallback, clearly
  labelled SAMPLE, never sold as live.
- CORS on the VM gateway is `*`; Caddy `tls internal` self-signed certs must
  be trusted by the visitor's browser before fetches stop failing.
- Never bundle any secret or real client PII; demo entities are fictitious.
- Keep template contract: `npm run build` → `dist/`, publish `dist/`, do not
  commit generated output.
