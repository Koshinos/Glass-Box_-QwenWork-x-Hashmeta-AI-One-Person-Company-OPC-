import type { Morning } from "../lib/api";
import { shortT } from "../lib/format";

export function Briefing({ m }: { m: Morning | null }) {
  if (!m) return <div className="empty"><b>Briefing not loaded yet.</b></div>;
  return (
    <div className="brief">
      <div className="bignums">
        <div className="bignum">
          <div className="n" style={{ color: "var(--block)" }}>{m.risk_actions_blocked}</div>
          <div className="l">Risky actions<br />blocked overnight</div>
        </div>
        <div className="bignum">
          <div className="n" style={{ color: "var(--owner)" }}>{m.fabricated_stats_flagged}</div>
          <div className="l">Fabricated numbers<br />flagged with evidence</div>
        </div>
        <div className="bignum">
          <div className="n" style={{ color: "var(--paper)" }}>{m.awaiting_one_click_approval}</div>
          <div className="l">Need your sign-off<br />(queue above)</div>
        </div>
        <div className="bignum">
          <div className="n" style={{ color: "var(--allow)" }}>{m.auto_allowed_verified}</div>
          <div className="l">Drafts auto-released,<br />every fact verified</div>
        </div>
      </div>
      <p style={{ margin: "0 0 6px" }}>
        ☕ Read time target: 15 seconds. The gateway acted on the rest —
        nothing here needed a second model's opinion.
      </p>
      {m.worst_catch && (
        <div className="worst">
          <div className="q">Worst tonight: <em>{prettyScenario(m.worst_catch.scenario)}</em></div>
          <div className="p">{firstClause(m.worst_catch.rule_path)}</div>
        </div>
      )}
      <p className="mtime" style={{ marginTop: 10, marginBottom: 0 }}>
        <span className="eyebrow" style={{ margin: 0 }}>
          generated {shortT(m.generated_at)} · SQL aggregation, zero generation
        </span>
      </p>
    </div>
  );
}

function prettyScenario(s: string | null): string {
  if (!s) return "an intercepted action";
  return s.replace(/^R\d+-/, "").replace(/-/g, " ");
}
function firstClause(p: string): string {
  return p.split("||")[0].split("|").slice(-1)[0].trim();
}
