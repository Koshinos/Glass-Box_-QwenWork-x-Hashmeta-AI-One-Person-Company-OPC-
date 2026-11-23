import { AUDIT, HEALTH, MORNING, PACK } from "./fixtures";

export interface EvidenceCard {
  claim: string;
  position: number;
  verdict: string;
  unit?: string;
  claim_value?: number;
  kg_value?: number;
  measure?: string;
  matched_node?: string;
  source_uri?: string;
  as_of_date?: string;
  effective_date?: string;
  type?: string;
}
export interface PackRow {
  scenario: string;
  name: string;
  action: string;
  expected: string;
  got: string;
  facts_flagged: number;
  result: string;
  rule_path: string[];
}
export interface Pack {
  score: string;
  false_positives_on_controls: number;
  deterministic_replay: boolean;
  rogue_scorecard: PackRow[];
  benign_controls: { scenario: string; got: string; result: string; facts_flagged: number }[];
}
export interface AuditRow {
  id: number;
  ts: string;
  draft_id: string;
  source: string;
  action: string;
  tier: string | null;
  decision: string;
  rule_path: string;
  evidence: EvidenceCard[] | string;
  draft_text: string | null;
  scenario: string | null;
  owner_status: string | null;
  facts_checked?: number | null;
  facts_flagged?: number | null;
  corrected?: string | null;
}
export interface Health {
  ontology_version: string;
  policy_cells: number;
  nodes: number;
  grounded_facts: number;
  deterministic: boolean;
  llm_in_decision_path: boolean;
  [k: string]: unknown;
}
export interface Morning {
  generated_at: string;
  risk_actions_blocked: number;
  fabricated_stats_flagged: number;
  awaiting_one_click_approval: number;
  auto_allowed_verified: number;
  worst_catch: { scenario: string | null; rule_path: string } | null;
}

export type Mode = "live" | "sample";

/* runtime base resolution: ?api= > localStorage > none (sample mode) */
export function readBase(): string {
  const q = new URLSearchParams(location.search).get("api");
  if (q) return q.replace(/\/+$/, "");
  return (localStorage.getItem("glassbox.api") || "").replace(/\/+$/, "");
}
export function writeBase(v: string) {
  if (v) localStorage.setItem("glassbox.api", v);
  else localStorage.removeItem("glassbox.api");
}

export interface Client {
  mode: Mode;
  health(): Promise<Health>;
  pack(): Promise<Pack>;
  audit(): Promise<AuditRow[]>;
  morning(): Promise<Morning>;
  decide(id: number, decision: "approve" | "reject"): Promise<{ ok: boolean }>;
}

async function get<T>(base: string, path: string, ms = 7000, init?: RequestInit): Promise<T> {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), ms);
  try {
    const r = await fetch(base + path, {
      ...init,
      signal: ac.signal,
      headers: { "content-type": "application/json", ...(init?.headers || {}) },
    });
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
    return (await r.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

const clone = <T>(v: T): T => JSON.parse(JSON.stringify(v));

function sampleClient(): Client {
  const audit = clone(AUDIT) as unknown as AuditRow[];
  return {
    mode: "sample",
    health: async () => clone(HEALTH) as Health,
    pack: async () => clone(PACK) as Pack,
    audit: async () => clone(audit),
    morning: async () => clone(MORNING) as Morning,
    decide: async (id, decision) => {
      const row = audit.find((r) => r.id === id);
      if (row) row.owner_status = `${decision === "approve" ? "approved" : "rejected"}:sample-local`;
      return { ok: true };
    },
  };
}

export function makeClient(base: string): Client {
  if (!base) return sampleClient();
  return {
    mode: "live",
    health: () => get<Health>(base, "/health"),
    pack: () => get<Pack>(base, "/simulate/rogue-pack", 25000, { method: "POST" }),
    audit: () => get<AuditRow[]>(base, "/audit?limit=50"),
    morning: () => get<Morning>(base, "/briefing/morning"),
    decide: (id, decision) =>
      get(base, `/audit/${id}/decide`, 8000, {
        method: "POST",
        body: JSON.stringify({ decision, note: "founder console" }),
      }).then(() => ({ ok: true })),
  };
}
