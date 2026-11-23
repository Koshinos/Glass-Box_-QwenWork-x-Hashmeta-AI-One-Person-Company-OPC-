import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { AuditRow, Health, Morning, Pack } from "./lib/api";
import { makeClient, readBase } from "./lib/api";
import { ConnectBar } from "./components/ConnectBar";
import { ScoreStrip } from "./components/ScoreStrip";
import { Queue } from "./components/Queue";
import { FactDiff } from "./components/FactDiff";
import { Briefing } from "./components/Briefing";

type Conn = "idle" | "live" | "sample" | "error";

export function App() {
  const [base, setBase] = useState(readBase());
  const client = useMemo(() => makeClient(base), [base]);
  const [conn, setConn] = useState<Conn>(base ? "idle" : "sample");
  const [error, setError] = useState("");
  const [health, setHealth] = useState<Health | null>(null);
  const [rows, setRows] = useState<AuditRow[]>([]);
  const [morning, setMorning] = useState<Morning | null>(null);
  const [pack, setPack] = useState<Pack | null>(null);
  const [running, setRunning] = useState(false);
  const [toast, setToast] = useState("");
  const toastTimer = useRef<number | null>(null);

  const say = useCallback((t: string) => {
    setToast(t);
    if (toastTimer.current) window.clearTimeout(toastTimer.current);
    toastTimer.current = window.setTimeout(() => setToast(""), 4000);
  }, []);

  const refresh = useCallback(async () => {
    try {
      const [h, a, m] = await Promise.all([
        client.health(), client.audit(), client.morning(),
      ]);
      setHealth(h); setRows(a); setMorning(m);
      setConn(client.mode === "live" ? "live" : "sample");
      setError("");
    } catch (e) {
      if (client.mode === "live") {
        setConn("error");
        setError(e instanceof Error ? e.message : "network error");
      } else {
        throw e;
      }
    }
  }, [client]);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    if (conn !== "live") return;
    const t = window.setInterval(() => void refresh(), 20000);
    return () => window.clearInterval(t);
  }, [conn, refresh]);

  const runPack = async () => {
    setRunning(true);
    try {
      const p = await client.pack();
      setPack(p);
      await refresh();
    } catch {
      say("Gateway didn’t answer during the run — the pack wasn’t executed.");
    } finally {
      setRunning(false);
    }
  };

  const decide = async (id: number, d: "approve" | "reject") => {
    await client.decide(id, d);
    if (client.mode === "sample")
      say("Decision recorded in sample mode only — nothing sent to your VM.");
    else say(`${d === "approve" ? "Approved" : "Rejected"} #${id} — gateway notified.`);
    await refresh();
  };

  return (
    <div className="shell">
      <ConnectBar
        base={base}
        health={health}
        state={conn}
        error={error}
        onConnect={(v) => {
          setBase(v);
          if (!v) { setConn("sample"); }
        }}
      />
      <main>
        <ScoreStrip pack={pack} running={running} onRun={runPack} />
        <div className="grid2">
          <section className="panel" aria-label="intercepted actions queue">
            <header>
              <h3>Intercepted Actions</h3>
              <span className="note">
                HARD_BLOCK + REQUIRE_OWNER · {rows.filter(r => r.decision !== "ALLOW").length} events
              </span>
            </header>
            <Queue rows={rows} onDecide={decide} />
          </section>
          <section className="panel" aria-label="fact check diff">
            <header>
              <h3>Fact-Check Diffs</h3>
              <span className="note">made-up number vs KG evidence</span>
            </header>
            <FactDiff rows={rows} />
          </section>
        </div>
        <div className="grid2" style={{ gridTemplateColumns: "1fr" }}>
          <section className="panel" aria-label="morning coffee briefing">
            <header>
              <h3>Morning Coffee Briefing</h3>
              <span className="note">GET /briefing/morning · 15-second read</span>
            </header>
            <Briefing m={morning} />
          </section>
        </div>
      </main>
      <footer className="legend">
        <div className="row">
          Sensitivity ramp:
          <span className="chip tier0">public</span>
          <span className="chip tier1">internal</span>
          <span className="chip tier2">client-confidential</span>
          <span className="chip tier3">regulated</span>
        </div>
        <div className="row">
          <span className="dot" style={{ background: "var(--block)" }} /> blocked
          <span className="dot" style={{ background: "var(--owner)" }} /> awaiting you
          <span className="dot" style={{ background: "var(--allow)" }} /> verified pass
        </div>
        <span className="motto">
          The graph decides. The founder decides. Nothing in between decides.
        </span>
      </footer>
      {toast && <div className="toast" role="status">{toast}</div>}
    </div>
  );
}
