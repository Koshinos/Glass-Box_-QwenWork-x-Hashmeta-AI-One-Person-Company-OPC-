import type { AuditRow } from "../lib/api";
import { friendlyNode, parsePath, shortT, TIER_RANK, verdictClass } from "../lib/format";

export function niceLabel(scenario: string | null, fallback: string): string {
  if (!scenario) return fallback;
  const [id, ...rest] = scenario.split("-");
  return rest.length
    ? id.toUpperCase() + " · " + rest.join(" ").replace(/-/g, " ")
    : id.toUpperCase() + " · " + fallback;
}

const DEC_WORD: Record<string, string> = {
  HARD_BLOCK: "Hard-blocked, no side effect",
  REQUIRE_OWNER: "Awaiting founder sign-off",
};

export function Queue({ rows, onDecide }: {
  rows: AuditRow[];
  onDecide: (id: number, d: "approve" | "reject") => void;
}) {
  const risky = rows
    .filter((r) => r.decision === "HARD_BLOCK" || r.decision === "REQUIRE_OWNER")
    .slice()
    .sort((a, b) => b.id - a.id);

  if (!risky.length)
    return (
      <div className="empty">
        <b>Nothing is waiting on you.</b>
        The queue stays quiet until an action touches confidential or regulated
        data — run the rogue pack to see it fill.
      </div>
    );

  return (
    <div className="body">
      {risky.map((r) => {
        const bc = parsePath(r);
        const tierN = TIER_RANK[bc.tier] ?? TIER_RANK[(r.tier || "").toLowerCase()] ?? 0;
        const uplift = bc.extras.find(
          (e) => e.includes("HARD_BLOCK") || e.includes("uplift") || e.includes("Exception")
        );
        return (
          <article className="queue-row" key={r.id}>
            <div className="crumbs" aria-label="ontology path">
              {bc.nodes.map((n, i) => (
                <span key={i}>
                  {i > 0 && <span className="arrow">→</span>}{" "}
                  <span className="chip node">{friendlyNode(n)}</span>
                </span>
              ))}
              {bc.more > 0 && (
                <span>
                  <span className="arrow">→</span>{" "}
                  <span className="chip node">+{bc.more} in closure</span>
                </span>
              )}
              <span className="arrow">→</span>{" "}
              <span className={`chip tier${tierN}`}>{bc.tier.replace(/_/g, "-")}</span>
              <span className="arrow">→</span>{" "}
              <span className="chip">{bc.action}</span>
              <span className="arrow">→</span>{" "}
              <span className={`verdict ${verdictClass(r.decision)}`}>
                {r.decision === "HARD_BLOCK" ? "BLOCKED" : "OWNER OK"}
              </span>
            </div>
            <div className="qmeta">
              <span className="sid">#{r.id}</span>
              <span>{shortT(r.ts)}</span>
              <span className="verdict" style={{ fontWeight: 500 }}>
                {DEC_WORD[r.decision] || r.decision.replace(/_/g, "-")}
              </span>
              <span>
                {niceLabel(r.scenario, r.draft_id)}
              </span>
              {typeof r.facts_checked === "number" && (
                <span>
                  · {r.facts_checked} facts checked
                  {r.facts_flagged
                    ? <span style={{ color: "var(--owner)" }}>, {r.facts_flagged} flagged</span>
                    : null}
                </span>
              )}
              {r.decision === "REQUIRE_OWNER" && (
                <span className="qactions">
                  {r.owner_status ? (
                    <span className="owner-done">{r.owner_status.split(":")[0]}</span>
                  ) : (
                    <>
                      <button className="mini ok" onClick={() => onDecide(r.id, "approve")}>
                        Approve
                      </button>
                      <button className="mini no" onClick={() => onDecide(r.id, "reject")}>
                        Reject
                      </button>
                    </>
                  )}
                </span>
              )}
              {r.decision === "HARD_BLOCK" && (
                <span className="sealed-note">▣ sealed — the call never left the gateway</span>
              )}
            </div>
            {uplift && <p className={"ruleline" + (uplift.includes("uplift") ? " uplift" : "")}>{uplift}</p>}
          </article>
        );
      })}
    </div>
  );
}
