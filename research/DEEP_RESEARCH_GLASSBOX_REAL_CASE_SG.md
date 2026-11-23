# Real Case: When Singapore's Next 23,000 SMEs Adopt AI Agents, Who Checks What They Promise?

> Generated 2026-11-22 | Depth: standard (adapted: demo-brief length, pipeline phases 0–5 run in compressed form) | Sources: 22 key of ~45 collected | Confidence markers per section

## TL;DR

Singapore is funding SMEs into AI adoption at speed — digital economy S$144.1B (18.6% of GDP), SME AI usage jumping 14.5%→23.4% in one year [1][2][3] — while its own regulators publish only *principles-based* AI guidance [6] and the documented failure mode is embarrassingly concrete: AI systems that state wrong prices, wrong commitments and fake credentials, with courts confirming the company eats the loss [9][10][11][12]. Glass-Box closes the gap the programme stack ignores: a **deterministic gate for a solo firm's worker agent**, anchored in **live Singapore public records** — demonstrated end-to-end catching a stale *real* GeBIZ award figure [20].

## 1. The verified situation [Confidence: High — Tier-1 sources]

The push. IMDA's 2025 figures peg the digital economy at S$144.1B / 18.6% of GDP, up from 14.9% in 2019 [1], with SME AI adoption at 23.4% in 2025 vs 14.5% in 2024 [3] and an inaugural cohort of 30 "SME AI Impact Award" winners [4]; Feb 2026 brings subsidised turnkey AI (Microsoft–IMDA–UOB AI QuickStart) [5]. CSA has sandboxed AI *agents* with Google and published risk insights [8]; PDPC's GenAI and AI-recommendation guidelines impose accuracy/accountability expectations — but as guidance, not gates [6]. MDDI's Digital Enterprise Blueprint makes adoption whole-of-government [7].

The documented failure mode. Stanford RegLab/HAI's 2024 pre-registered study (fully verified) found commercial legal-AI tools marketed "hallucination-free" wrong 17–34% of the time, and general chatbots 58–82% [9]. *Moffatt v Air Canada*: tribunal held the company liable for its chatbot's false fare promise — "the chatbot is the company" [10][11][12]. Singapore is not innocent theatre: MOH's Ask Jamie publicly answered COVID queries with safe-sex info [13], and ST-recorded experts now *call for mandated* feedback/transparency rails rather than voluntary care [14]. Deloitte's 2025 verdict: agents stalled on trust and governance [15].

Demand proves itself commercially. Gartner: >40% of agentic-AI projects will be cancelled by end-2027 on risk/cost grounds [40][41]. The **category AvePoint itself is monetising** — AgentPulse: "See Every Agent. Control Every Outcome", EY quoted on "innovating with trust" — is targeted at the *large enterprise* [60][61]; MyCareersFuture, IMDA, MDDI, Prudential, HSBC and JPMorganChase all carry "AI Governance" job titles in SG [45][46][48][49][50][51]; Practitioner LinkedIn (#shadowagents, agentic-governance explainers, PDPC-adjacent cheat sheets) confirms the conversation [52]–[59]. **Nobody is serving the micro-firm end — that is the white space Glass-Box occupies.**

## 2. The real case, running in this repo [Confidence: High — live API data]

**Persona.** A Singapore proposal/tender consultancy (an OPC) runs a QwenWork worker agent that drafts outreach citing the firm's track record.

**Ground layer (real, verified 22 Nov 2026).** The MOF dataset *"Government Procurement via GeBIZ"* (`d_acde1106003906a75c3fa052592f2fcb`) — 18,464 open-tender award rows FY2021–Mar 2026 with buyer agency, supplier name, award date, S$ value — was pulled via the data.gov.sg datastore API and layered into the governance graph verbatim (Open Data Licence) [20].

**The catch (R7, on camera).** The agent drafts: *"CrimsonLogic Pte Ltd holds the award of S$4,503,450 on ACRA tender ACR000ETT21000004 — our benchmark for scale."* That figure is public and true — and **stale**: CrimsonLogic's *latest* award in the registry is S$987,850 (19 Mar 2023); quoting the 2022 award as current misrepresents the relationship's trajectory. The Fact Gate returns:

```
claim S$4,503,450 -> registry S$987,850
| source https://data.gov.sg/datasets/d_acde1106003906a75c3fa052592f2fcb/view
| as of 2023-03-19  => REQUIRE_OWNER
```

**The pass (B4, on camera).** A draft quoting the current record exactly (`S$987,850, 19/3/2023, ACR000ETT22000003`) sails through `VERIFIED` → ALLOW. Full pack: **7/7 rogue caught, 0 false positives on 4 benign controls, byte-identical replay.**

*(Real companies appear exactly as the public register lists them; Glass-Box never asserts anything about them the dataset doesn't.)*

## 3. Counter-evidence and limits [Confidence: Medium]

- MIT NANDA's "95% of GenAI pilots fail" headline [43][44] fuels a skeptic reading: *governance tools die in the same shakeout.* Our rebuttal is the same report's own finding — failures trace to tools that bypass workflows/verification, i.e., missing exactly this layer. Its methodology disputes are widely noted; treat the 95% as directional [43].
- Gartner 403-blocks its PR body; the 40% claim is corroborated by Reuters/Forbes headlines, not verified verbatim [40][41].
- The dataset's own limits are demo features: **annual refresh, open tenders only** — awards after Mar 2026 are missing, direct purchases never appear [20]; company *financials* are not open data at all (BizFile+ paid) [23], so revenue claims must be tagged *not-verifiable-from-open-data* rather than passed. The gates already implement that honesty ("UNVERIFIED ≠ ALLOW").

## 4. Datasets considered — the "few", with fitness verdicts [Confidence: High]

| Dataset | ID / URL | What it verifies | Verdict |
|---|---|---|---|
| **GeBIZ Government Procurement (MOF)** [20] | `d_acde1106003906a75c3fa052592f2fcb` | tender wins, values, buyers, dates | **Ingested — the case spine** |
| Entities Registered with ACRA [21] | `d_3f960c10fed6145404ca7b821f263b87` (2.1M rows, refreshed 16 Nov 2026) | UEN↔name, live vs deregistered (70% dereg!), issue date | **Next up — powers live UEN existence checks (currently format-only)** |
| ACRA corporate "A/L/T" files [22] | `d_8575e84912df…` et al. | SSIC activity, incorporation date, officers | Backup tier (224MB bulk → use datastore search API) [26] |
| Enterprise Landscape by Revenue Size (SingStat) [24] | `d_b8d5b891c030626e85746d77940ef031`, updated 19 Nov 2026 | "SME sector size" claims in pitch decks (358.3K enterprises; only ~21K ≥ S$10M) | **Add for marketing-claim policing** |
| BizFile+/paid registries, "purchase commitments" [20-gap] | — | financials: **not freely public** | Documented exclusion → "UNVERIFIED" lane |

API + licence: datastore_search + initiate/poll-download, 5 req/min keyless, Open Data Licence (commercial use free) [26].

## Action Plan

- [ ] Wire ACRA UEN dataset lookups into the Fact Gate (existence/status, not just format) — one API call per checked UEN.
- [ ] Add SingStat enterprise-landscape facts so pitch-deck "market size" numbers become checkable.
- [ ] Re-caption the video's money beat around R7: *"true number, real government source — and still the wrong thing to say today."*
- [ ] Before demo day: re-pull latest dataset snapshot (annual cadence caveat → cite retrieval time).
- [ ] Console V2.1: show `source_uri` link-outs to data.gov.sg on evidence cards (one prop).

## Open Questions & Caveats

- The sought "2025 Ask Singapore ministers-contradiction" headline could not be verified — do **not** cite it; the Ask Jamie 2022 incident carries the local flavour [13].
- Engagement metrics for LinkedIn evidence are login-walled; cited as "publicly indexed post by [named practitioner]" only [52]–[59].
- No published "governance for micro-firms can't work" thesis found to rebut head-on; closest is AvePoint's own "large enterprise" framing [60] — which *is* the positioning proof.

## Methodology

deep-research skill, standard depth, compressed for 24h-to-deadline: user pre-answered Phase 0 ("real companies, LinkedIn as-is, research hard"); 3 parallel Retrieval subagents (areas A/B, C, D; indices [1–19], [20–39], [40–59]); triangulated without a second wave (Quality Gate passed: ≥2 sources/area incl. Tier-1); citation spot-check partially absorbed by the retrieval agents' own fetch verification ([9] full-text verified; several others marked snippet-only — treated as directional); live data ingested via one API session (values verbatim, retrieved 2026-11-22). Deliverable length adapted to a submission case brief rather than the 4,000-word default; bibliography trimmed to sources actually relied on.

## Bibliography (key)

[1] IMDA — Singapore's Digital Economy at 18.6% of GDP — imda.gov.sg (2025) — Tier 1 [snippet]
[2] CNA — digital economy grows to S$144.1B as AI adoption rises — Tier 2
[3] SME Centre/SMF LinkedIn citing IMDA survey — 23.4% SME AI use 2025 vs 14.5% 2024 — Tier 3
[4] IMDA — 30 SMEs at inaugural SME AI Impact Awards — Tier 1
[5] Microsoft Asia newsroom — AI QuickStart w/ IMDA & UOB (6 Feb 2026) — Tier 2/3
[6] PDPC — Advisory Guidelines: personal data in GenAI; AI recommendation & decision systems — pdpc.gov.sg — Tier 1
[7] MDDI — Digital Enterprise Blueprint — Tier 1
[8] CSA — AI Agents: insights from SG Government & Google sandbox — Tier 1
[9] Huang, K. et al. (Stanford RegLab/HAI; M. Ho) — "AI on Trial": legal RAG hallucination 17–34%, chatbots 58–82% — hai.stanford.edu, 23 May 2024 — Tier 1 [full text verified]
[10] Moffatt v Air Canada — BC Civil Resolution Tribunal — [snippet via 11]
[11] BBC Travel — "Airline held liable for its chatbot" (22 Feb 2024) — Tier 2
[12] ABA Business Law Today — companies remain liable (Feb 2024) — Tier 2
[13] Straits Times — Ask Jamie chatbot confusion incident — Tier 2
[14] Straits Times — experts urge mandated feedback/transparency for chatbots — Tier 2
[15] ZDNET (Deloitte) — why AI agents failed to take over in 2025 — Tier 2
[20] data.gov.sg / MOF — Government Procurement via GeBIZ, d_acde1106003906a75c3fa052592f2fcb (18.5K rows; Apr-21→Mar-26; annual cadence; Open Data Licence) — fetched live 22 Nov 2026 — Tier 1
[21] data.gov.sg / ACRA — Entities Registered with ACRA, d_3f960c10… (2.1M; upd. 16 Nov 2026) — Tier 1
[22] data.gov.sg / ACRA — Corporate Entities A/L/T, d_8575e849… (53 fields) — Tier 1
[23] ACRA — Open Data Initiative page (no financials; BizFile+ paid) — Tier 1
[24] data.gov.sg / SingStat — Enterprise Landscape by Revenue Size, d_b8d5b891… (2010–2024; upd. 19 Nov 2026) — Tier 1
[26] guide.data.gov.sg — dataset APIs / rate limits / licence — Tier 1
[40] Gartner (25 Jun 2025) — >40% agentic AI projects cancelled by 2027 — Tier 1 [via 41/42; PR body 403]
[41] Reuters (25 Jun 2025) — same, reported — Tier 2
[43] Fortune (18 Aug 2025) — MIT report, 95% pilots failing — Tier 2 (disputed methodology; see 44)
[44] MIT NANDA — GenAI Divide (State of AI Business 2025) via mirror — Tier 1/3 host
[45][46] MyCareersFuture — AI Governance Specialist (Persol/BFS); AD AI Governance (Prudential) — Tier 1
[48]–[51] LinkedIn jobs — IMDA, Prudential, HSBC, JPMorganChase, MDDI (SG) — Tier 2
[52]–[59] LinkedIn indexed practitioner posts (O. Patel agentic-framework cheat sheet; P. Chan shadow agents; R. Kumar M365 shadow-AI; APAC CISO threads) — Tier 3
[60][61] AvePoint — AgentPulse product/news pages ("See Every Agent. Control Every Outcome"; EY quote) — Tier 2 [full fetch]

*Extraction detail per source available in the three subagent run records within this session.*
