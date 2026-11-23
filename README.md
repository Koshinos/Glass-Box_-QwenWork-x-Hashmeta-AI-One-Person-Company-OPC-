# Glass-Box AI Governance Gateway — Complete Package
**AvePoint Track 2 (AI Governance) submission kit · prepared 22–23 Nov 2026**

> A deterministic, graph-backed governor for a solo firm's AI worker agent.
> Three gates — **Policy** (sensitivity tiers), **Fact** (ledger + real public
> records), **Promise** (effective-dated terms with client-scoped grandfathering).
> **Zero LLM calls in any verdict. 7/7 rogue scenarios caught, 0 false positives
> across 4 benign controls, byte-identical replay.**

## Live surfaces (verify with your own eyes)

| Surface | URL |
|---|---|
| Founder oversight console (QwenWork Page) | https://u9s7arc3.qwenwork.page/ |
| Public site the graph polices (Hashmeta AI) | https://glassbox.geo.hashmeta.tech |
| Terms Registry Change Log (graph-drafted, live) | https://glassbox.geo.hashmeta.tech/registry-change-log |

## Folder map

```
GlassBox-Package/
├── backend/        FastAPI governance gateway for the QwenWork Agent Computer
│   ├── oversight.py       policy matrix + fact gate + promise gate + /send /impact
│   ├── db_init.sql        kg_nodes · kg_edges · policy_rules · audit_log
│   ├── db_seed.sql        10 SG-shaped demo records + full policy matrix + temporal terms
│   ├── db_realdata.sql    REAL GeBIZ award rows (data.gov.sg, 22 Nov 2026, verbatim)
│   ├── hashmeta_mcp.py    OAuth2.1/PKCE MCP client (151 tools)
│   ├── oauth_capture.py   consent flow runner
│   ├── campaign_loop.py   registry-drift closed loop (queue→approve→verify)
│   ├── prove_six.py       one-shot proof chain
│   ├── Caddyfile · run-gateway.sh · requirements.txt
├── engine/         the original deterministic engine (schema.sql, seed, gates,
│                   tests/rogue_scenarios.py → 5/5 offline replay, README-free)
├── console-src/    Founder Console V2 — Vite+React+TS (QwenWork Pages source repo;
│                   live at the URL above; `npm i && npm run preview` to run)
├── research/       DEEP_RESEARCH_GLASSBOX_REAL_CASE_SG.md (22 cited sources,
│                   confidence labels, dataset inventory with fitness verdicts)
├── pamphlet/       User pamphlet: PDF (A4 double-sided, print-ready) + HTML source
└── submission/     VIDEO_SCRIPT.md (3:00, rubric-timed), screenshots/,
                    SCORECARD_FINAL.txt, loop_ledger.jsonl (closed-loop audit trail)
```

## Quickstart (Python 3.10+, no DB server, no Neo4j)

```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn oversight:app --port 8000
# in another terminal:
curl -XPOST localhost:8000/simulate/rogue-pack          # -> 7/7, controls ok
curl localhost:8000/impact | python3 -m json.tool       # -> scans the real live site
```
Then open the console, paste `http://localhost:8000` into the Connect bar → LIVE.

## What's fiction (say it first, own it)
- Clients/personas (NusaGov, SensoCore, Nexgate…), the S$900 planted lie, and
  two GeBIZ scenario rows are **fictitious**, in real ACRA/GeBIZ/NRIC formats.
- The 8 supplier/tender rows in `db_realdata.sql` are **real public records**,
  verbatim from MOF's GeBIZ open dataset; each carries its `source_uri`.
- `backend/.glassbox/` (OAuth tokens) is deliberately **not shipped**.

## Known open items (do not claim these are done)
- Scheduled morning-brief **push** to Slack/DingTalk: console briefing panel is
  live and data-driven; the connector task was not created before freeze.
- SEO site-audit tool: not exposed via MCP (reports consume, don't trigger).
- Second AI-writer seat: blocked on Hashmeta trial quota (1 allowed).
