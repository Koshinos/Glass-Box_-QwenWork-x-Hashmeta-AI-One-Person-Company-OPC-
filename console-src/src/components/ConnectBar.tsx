import { useEffect, useState } from "react";
import type { Health } from "../lib/api";
import { readBase, writeBase } from "../lib/api";

interface Props {
  base: string;
  health: Health | null;
  state: "idle" | "live" | "sample" | "error";
  error?: string;
  onConnect: (v: string) => void;
}

export function ConnectBar({ base, health, state, error, onConnect }: Props) {
  const [draft, setDraft] = useState(base);
  useEffect(() => setDraft(base), [base]);

  const pill =
    state === "live" ? <span className="pill live">● LIVE · gateway connected</span>
    : state === "error" ? <span className="pill err">● GATEWAY UNREACHABLE</span>
    : <span className="pill sample">◆ SAMPLE · embedded cold-run capture</span>;

  return (
    <header className="topbar">
      <div className="brand">
        <div className="monogram" aria-hidden>GB</div>
        <div>
          <p className="eyebrow">Deterministic AI governance · Singapore OPC</p>
          <h1>Glass-Box <em>Oversight</em> Console</h1>
        </div>
      </div>
      <div className="connect">
        {pill}
        <input
          aria-label="Agent Computer gateway URL"
          placeholder="https://&lt;your-agent-computer&gt; — paste gateway URL"
          value={draft}
          spellCheck={false}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") commit(draft, onConnect); }}
        />
        <button className="mini ok" onClick={() => commit(draft, onConnect)}>Connect</button>
        {base && <button className="mini no" onClick={() => onConnect("")}>Clear</button>}
      </div>
      {state === "error" && (
        <p style={{ width: "100%", margin: 0, color: "var(--owner)", fontSize: 12.5 }}>
          {error || "The gateway didn’t answer."} Check: URL starts with https://, the VM
          process is running, and (for Caddy self-signed certs) you have opened the
          gateway URL once in this browser and trusted it.
        </p>
      )}
      {health && (
        <div className="healthline" style={{ width: "100%", margin: "14px 0 0" }}>
          <span><b>{health.policy_cells}</b> policy cells loaded (gap ⇒ request aborts)</span>
          <span><b>{health.nodes}</b> graph nodes · <b>{String((health as Record<string, unknown>).grounded_facts ?? "—")}</b> grounded facts</span>
          <span className="ok"><b>{health.llm_in_decision_path ? "LLM" : "0"}</b> LLM calls in the decision path</span>
          <span>ontology <b>{health.ontology_version}</b></span>
          <span>{state === "sample" ? "verdicts shown are the archived run’s — connect your VM for live" : "connected live to the Agent Computer"}</span>
        </div>
      )}
    </header>
  );
}

function commit(v: string, onConnect: (v: string) => void) {
  const clean = v.trim().replace(/\/+$/, "");
  writeBase(clean);
  onConnect(clean);
}
