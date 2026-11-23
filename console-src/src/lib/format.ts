import type { AuditRow, EvidenceCard } from "./api";

export const TIER_LABEL: Record<string, string> = {
  public: "public",
  internal: "internal",
  client_confidential: "client-confidential",
  regulated: "regulated",
};
export const TIER_RANK: Record<string, number> = {
  public: 0, internal: 1, client_confidential: 2, regulated: 3,
};
const VERDICT_CLASS: Record<string, string> = {
  ALLOW: "v-allow", REQUIRE_OWNER: "v-owner", HARD_BLOCK: "v-block",
};

export function friendlyNode(id: string): string {
  const tail = id.includes(":") ? id.split(":").slice(1).join(":") : id;
  return tail;
}

export interface Breadcrumbs {
  nodes: string[];
  more: number;
  tier: string;
  action: string;
  decision: string;
  text: string;
  extras: string[];
}

/** Parses the matrix line of rule_path[0]; sub-lines (recipient checks,
 *  fact uplifts) return as extras. Never guesses — falls back honestly. */
export function parsePath(row: AuditRow): Breadcrumbs {
  const lines = String(row.rule_path).split(" || ");
  const head = lines[0] || "";
  const m = head.match(/^(?<n>.*?)\s\[closure(?:[^\]]*)\]\s*->\s*tier=(?<tier>\w+),\s*action=(?<action>\w+)\s*=>\s*(?<dec>\w+)\s*\|\s*(?<text>.*)$/);
  if (!m?.groups) {
    return {
      nodes: [friendlyNode(row.draft_id)], more: 0,
      tier: row.tier || "unknown", action: row.action,
      decision: row.decision, text: head, extras: lines.slice(1),
    };
  }
  const ids = m.groups.n.split(",").map((s) => s.trim()).filter(Boolean);
  return {
    nodes: ids.slice(0, 3), more: Math.max(0, ids.length - 3),
    tier: m.groups.tier, action: m.groups.action, decision: m.groups.dec,
    text: m.groups.text, extras: lines.slice(1),
  };
}

export function verdictClass(d: string): string {
  return VERDICT_CLASS[d] || "v-owner";
}

export function parseEvidence(row: AuditRow): EvidenceCard[] {
  if (typeof row.evidence === "string") {
    try { return JSON.parse(row.evidence) as EvidenceCard[]; } catch { return []; }
  }
  return row.evidence || [];
}

export const FLAGGED = new Set([
  "FACT_CONTRADICTION", "PROMISE_CONFLICT", "UNKNOWN_UEN",
  "REGULATED_PII_PRESENT", "UNKNOWN_PII",
]);

export function money(v?: number, unit?: string): string {
  if (v === undefined) return "—";
  if (unit === "PCT") return `${v}%`;
  if (unit === "DAYS") return `${v} days`;
  return `S$${v.toLocaleString("en-SG", { maximumFractionDigits: 2 })}`;
}

export function relDiff(c?: number, k?: number): string | null {
  if (c === undefined || k === undefined || !k) return null;
  const r = c / k;
  if (r >= 1.05) return `claimed ×${r.toFixed(2)} the real value`;
  if (r <= 0.95) return `claimed ×${r.toFixed(2)} the real value`;
  return `${((r - 1) * 100).toFixed(1)}% off`;
}

export function shortT(ts: string): string {
  return (ts || "").slice(11, 19);
}
