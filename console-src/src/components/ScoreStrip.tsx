import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import type { Pack } from "../lib/api";
import { niceLabel } from "./Queue";

export function ScoreStrip({
  pack, running, onRun,
}: { pack: Pack | null; running: boolean; onRun: () => void }) {
  const [animate, setAnimate] = useState(false);
  useEffect(() => {
    if (pack) {
      setAnimate(true);
      const t = setTimeout(() => setAnimate(false), 400 * tileCount(pack) + 600);
      return () => clearTimeout(t);
    }
  }, [pack]);
  const tileCount = (p: Pack) => p.rogue_scorecard.length + p.benign_controls.length;

  const missed = pack
    ? pack.rogue_scorecard.filter((r) => r.result !== "PASS").length
    : null;
  const caught = pack ? pack.rogue_scorecard.length - missed! : null;
  const total = pack ? pack.rogue_scorecard.length : 0;

  return (
    <section className={"hero" + (animate ? " animate" : "")} aria-label="rogue pack">
      <p className="eyebrow">Rogue-pack stress test · AvePoint Track 2 scenario harness</p>
      <h2>
        {pack ? (
          <>
            {total} scripted misbehaviours.{" "}
            <span className="caught">{caught} caught.</span>{" "}
            {missed === 0 ? <>Zero missed violations.</> : <>  {missed} missed — fix the graph.</>}
          </>
        ) : (
          <>Send scripted rogue agents at the gateway. Watch every one get stopped, in writing.</>
        )}
      </h2>
      <p className="sub">
        One click calls <code>POST /simulate/rogue-pack</code> on your Agent Computer.
        Every verdict is a table lookup plus a graph walk — replay it on camera,
        the answer never drifts.
      </p>
      <div className="runrow">
        <button className="run" onClick={onRun} disabled={running}>
          {running ? "Replaying the pack…" : "Run Rogue Pack (6 scenarios)"}
        </button>
        <div className={"scorebadge" + (pack ? "" : " pending")}>
          <span className={"big" + (pack && missed === 0 ? " zero" : "")}>
            {pack ? pack.score : "—"}
          </span>
          <span className="label">
            Violations caught
            <br />
            {pack
              ? missed === 0
                ? "0 missed · 0 benign blocks"
                : `${missed} missed — do not ship`
              : "awaiting run"}
          </span>
        </div>
      </div>

      <div className="seals">
        {(pack
          ? [
              ...pack.rogue_scorecard.map((r) => ({
                key: r.scenario,
                id: r.scenario.split("-")[0],
                name: niceLabel(r.scenario, r.name),
                stamp:
                  r.result !== "PASS" ? "MISSED"
                    : r.expected === "HARD_BLOCK" ? "SEIZED" : "HELD",
                cls: r.result !== "PASS" ? "leaked" : r.expected === "HARD_BLOCK" ? "seized" : "held",
              })),
              ...pack.benign_controls.map((c) => ({
                key: c.scenario,
                id: c.scenario.split("-")[0],
                name: niceLabel(c.scenario, "benign control"),
                stamp: c.result === "PASS" ? "CLEARED" : "FRICTION",
                cls: c.result === "PASS" ? "cleared" : "leaked",
              })),
            ]
          : PLACEHOLDER_TILES
        ).map((t, i) => (
          <div
            className={"tile " + (t.stamp ? t.cls : "")}
            key={t.key}
            style={{ "--i": String(i) } as CSSProperties}
          >
            <div className="id">{t.id}</div>
            <div className="what">{t.name}</div>
            {t.stamp && (
              <div className="stamp" aria-label={t.stamp}>
                <span>{t.stamp}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

const PLACEHOLDER_TILES = [
  ...["R1", "R2", "R3", "R4", "R5", "R6"].map((id) => ({
    key: id, id, name: "scripted misbehaviour", stamp: "", cls: "",
  })),
  ...["B1", "B2"].map((id) => ({
    key: id, id, name: "benign control", stamp: "", cls: "",
  })),
];
