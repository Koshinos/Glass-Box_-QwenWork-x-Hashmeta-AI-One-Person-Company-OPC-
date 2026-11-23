-- governance_kg.db — Prompt A schema (4 tables, nothing else)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS kg_nodes (
  id    TEXT PRIMARY KEY,
  name  TEXT NOT NULL,
  type  TEXT NOT NULL,     -- tender|client|sop|proposal|record|benchmark
  tier  TEXT NOT NULL CHECK (tier IN ('public','internal','client_confidential','regulated')),
  props TEXT NOT NULL DEFAULT '{}'   -- JSON: uen, facts{measure:value}, source_uri,
                                     -- as_of_date, authorized_recipients[...]
);

CREATE TABLE IF NOT EXISTS kg_edges (
  src TEXT NOT NULL REFERENCES kg_nodes(id),
  rel TEXT NOT NULL,                  -- references | pertains_to
  dst TEXT NOT NULL REFERENCES kg_nodes(id),
  PRIMARY KEY (src, rel, dst)
);

-- action '*' = rule for every action class (wildcard loses to a specific row).
CREATE TABLE IF NOT EXISTS policy_rules (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  tier       TEXT NOT NULL,
  action     TEXT NOT NULL,
  decision   TEXT NOT NULL CHECK (decision IN ('ALLOW','REQUIRE_OWNER','HARD_BLOCK')),
  rule_text  TEXT NOT NULL,
  UNIQUE (tier, action)
);

CREATE TABLE IF NOT EXISTS audit_log (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts           TEXT NOT NULL,
  draft_id     TEXT NOT NULL,
  source       TEXT NOT NULL DEFAULT 'worker-agent',
  action       TEXT NOT NULL,
  tier         TEXT,
  decision     TEXT NOT NULL,
  rule_path    TEXT NOT NULL,
  evidence     TEXT NOT NULL DEFAULT '[]',   -- JSON fact cards
  corrected    TEXT,                          -- Promise Gate deterministic rewording
  facts_checked  INTEGER NOT NULL DEFAULT 0,
  facts_flagged  INTEGER NOT NULL DEFAULT 0,
  draft_text   TEXT,
  scenario     TEXT,                          -- set by the rogue-pack harness
  owner_status TEXT,                          -- approved:<ts> | rejected:<ts>
  owner_note   TEXT
);
