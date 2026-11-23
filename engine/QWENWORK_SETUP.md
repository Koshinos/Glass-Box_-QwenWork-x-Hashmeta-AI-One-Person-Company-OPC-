# Glass-Box Governance Gateway — QwenWork Sprint Runbook (AvePoint Track 2)

Deadline 23 Nov 2026. Everything in `kg/` + `tests/` is done and passing:
`python3 tests/rogue_scenarios.py` → **5/5 rogue caught, 2/2 benign controls pass,
exit code 0.** The engine needs no internet, no pip installs, no Neo4j.

## What you already have (this folder)

| File | Role |
|---|---|
| `kg/schema.sql` | Ontology: tiers, actions, exhaustive 4×7 policy matrix, nodes/edges, facts w/ provenance, recipients, audit log |
| `kg/seed.sql` | All 28 policy cells + SG-shaped ground truth (UENs, GeBIZ award, SingStat PPI, mock invoices) |
| `kg/policy_gate.py` | Deterministic traversal: tier inheritance (max-rank, hop-capped), fail-closed matrix, Authorized-Recipient Exception |
| `kg/fact_gate.py` | Regex→SQL fact-check: S$ amounts, %, ACRA-format UENs → VERIFIED / FACT_CONTRADICTION / UNKNOWN_UEN / UNVERIFIED cards |
| `kg/engine.py` | Composer: `final = max(policy, fact_uplift)`, writes `interception_log`, SQL `digest()` |
| `kg/server.py` | Stdlib JSON API on :3000 — `/intercept /log /digest /owner_action /health` |
| `tests/rogue_scenarios.py` | The 5/5 scorecard to film |

Honest data note (say this in the video, judges love it): entity/fact rows are
fictitious demo clients in **real ACRA/GeBIZ/SingStat formats**; `source_uri`
uses `demo://` until the VM live-fetcher replaces them (step 1 below). No real
company is attributed fake numbers anywhere.

## Step 1 — Agent Computer (always-on VM backend)

Create a QwenWork session on an Agent Computer and paste:

> Upload the `glassbox-kg/` folder to the VM at `~/gateway/`. Install nothing —
> it is stdlib-only. Start `python3 kg/server.py` as a persistent process on
> port 3000 and have it restart on reboot. Add a script
> `kg/live_fetch.py` that pulls real rows from data.gov.sg (ACRA UEN lookup,
> SingStat producer price index) and the GeBIZ opportunities site for the demo
> entities, writes them into the `fact` table with the live `source_uri` and
> `as_of_date`, and re-runs `tests/rogue_scenarios.py` so the matrix never
> drifts. Then expose the gateway URL.

## Step 2 — Worker agent + interceptor hook

On the same VM, create the worker (research/tender/outreach) and give it this
standing rule in its instructions:

> Before ANY tool call that sends email, posts publicly, uploads to a third
> party, moves money, or signs, POST the draft to
> `http://localhost:3000/intercept` with `{draft_id, action, text,
> payload_ids, recipient_emails}`. You may execute only on `decision: ALLOW`.
> On `REQUIRE_OWNER`, park the draft in the console queue and continue other
> work. On `HARD_BLOCK`, stop, and report the rule_path to the requester.
> Never rephrase a blocked request to sneak it through; that attempt itself
> must be logged.

That quote + the passing scorecard is the "LLM policing deterministic graph
policy, not LLM policing LLM" line for your narration.

## Step 3 — Founder Oversight Console (QwenWork Pages, dynamic)

Vibe-code prompt for the Pages app (dynamic; DB optional since state lives on
the VM):

> Build a one-page console that proxies the VM gateway (do NOT store policy
> state twice). Panels: (1) interception feed with decision colour-coding:
> BLOCKED red, AWAITING OWNER amber, PASSED green; (2) per-item "Why" drawer
> rendering `rule_path` as an Ontology breadcrumbs line
> `Entity -> client-confidential -> external_send -> BLOCKED`; (3) Evidence
> cards: claimed number vs grounded KG number, source_uri, as_of_date,
> source system badge; (4) 1-click Approve/Reject calling `/owner_action`;
> (5) header stats from `/digest`; (6) `/health` badge showing
> `policy_cells: 28/28 COMPLETE` — the zero-fall-through proof.

## Step 4 — Morning Coffee Briefing (Scheduled Task + Connector)

Scheduled Task, daily 08:15 SGT, prompt:

> `GET /digest` and the 24h rows of `GET /log`. Compose exactly this shape and
> send via the Slack (or WhatsApp) connector:
> "☕ Oversight overnight — X risky actions BLOCKED, Y fabricated stats sent to
> you for decision, Z drafts auto-approved with all facts verified. Worst catch:
> <one-line rule_path>. Zero LLM judgement involved; reply APPROVE <id> to
> release one item." Keep it under 15 seconds of reading time.

## Step 5 — Rubric checklist (do not skip #1)

1. **Hashmeta AI site (15%)** — landing page w/ AI CMS + lead capture, early,
   independent of everything else.
2. **3-min video, moments in order:** 0:00 setup + "5/5" scorecard terminal
   frame (re-run `tests/rogue_scenarios.py` live — it's deterministic, so the
   take can't fail); 0:30 R1/R2 interception with ontology breadcrumbs in the
   console; 1:15 R3/R4 evidence card (12.5M claim vs 8.5M ledger / 1.2M vs
   GeBIZ 412k); 2:00 Slack digest; 2:40 console URL + Hashmeta URL.
3. **Judging emphasis line to land:** zero missed violations > clever UI —
   demoed by the fail-closed matrix (28/28 cells) + unknown-recipient = -1
   ceiling + replay determinism.

## Known limits (for Q&A honesty)

- Fact Gate keywords are tuned to the scenario pack's phrasing; generalization
  is a documented backlog item, not hidden behind "AI magic".
- Cross-checking `UNVERIFIED` numbers is advisory-only (flagged, not blocked) —
  deliberate: blocking every unknown number would train the founder to rubber-
  stamp. Say exactly that; it's the false-positive-control argument.
- Recipient identities are `.example` mockmail; connector demo uses Slack
  sandbox channel.

Next available builds: the Pages console HTML (I can generate it now), or the
`live_fetch.py` data.gov.sg loader once you confirm the VM session exists.
