import type { AuditRow, EvidenceCard } from "../lib/api";
import { FLAGGED, money, parseEvidence, relDiff } from "../lib/format";

export function FactDiff({ rows }: { rows: AuditRow[] }) {
  const cards: { row: AuditRow; card: EvidenceCard }[] = [];
  for (const row of rows) {
    for (const card of parseEvidence(row)) {
      if (FLAGGED.has(card.verdict)) cards.push({ row, card });
    }
  }
  if (!cards.length)
    return (
      <div className="empty">
        <b>No open contradictions.</b>
        Every number that left this gateway in a risky draft matched verified
        ground truth and current published terms at check time.
      </div>
    );

  return (
    <div className="body">
      {cards.slice(0, 6).map(({ row, card }, i) => {
        const isPromise = card.verdict === "PROMISE_CONFLICT";
        const isNum = card.verdict === "FACT_CONTRADICTION" || isPromise;
        return (
          <section className="diff" key={i}>
            <div className="head">
              <span>#{row.id} · {row.scenario || row.draft_id}</span>
              <span className="where">
                {isPromise
                  ? "commitment drift — checked against effective-dated terms"
                  : "checked when the draft went out, not after"}
              </span>
            </div>
            <div className="pair">
              <div className="half claim">
                <p className="tag">Worker agent asserted</p>
                <p className="num">{card.claim}</p>
                <p className="ratio">
                  {isNum
                    ? relDiff(card.claim_value, card.kg_value) ?? ""
                    : card.verdict === "UNKNOWN_UEN"
                      ? "format-valid ACRA UEN, zero graph hits"
                      : card.verdict.includes("PII")
                        ? "matches a regulated NRIC sample on file"
                        : ""}
                </p>
              </div>
              <div className="vs" aria-hidden />
              <div className="half truth">
                <p className="tag">
                  {isPromise ? "Current effective terms" :
                    isNum ? "Verified KG node" :
                      card.verdict === "UNKNOWN_UEN" ? "Ground truth says" : "PDPA register"}
                </p>
                <p className="num">
                  {isNum ? money(card.kg_value, card.unit)
                    : card.verdict === "UNKNOWN_UEN" ? "no match" : card.claim}
                </p>
                {isNum ? (
                  <p className="why">
                    <code>{card.measure}</code>{" "}
                    {card.effective_date
                      ? <>· since <code>{card.effective_date}</code></>
                      : card.as_of_date
                        ? <>· as of <code>{card.as_of_date}</code></> : null}
                    <br />
                    <span title="source recorded with the term">{card.source_uri}</span>
                  </p>
                ) : (
                  <p className="why">
                    {card.verdict === "UNKNOWN_UEN"
                      ? <>UEN <code>{card.claim}</code> is not in the verified ACRA layer — an invented detail; never guess-send it.</>
                      : <>Regulated sample value appears verbatim in a draft body — PII in the payload is itself the violation.</>}
                  </p>
                )}
                {isPromise && row.corrected && (
                  <p className="why fix">✓ corrected wording: “{row.corrected}”</p>
                )}
              </div>
            </div>
          </section>
        );
      })}
    </div>
  );
}
