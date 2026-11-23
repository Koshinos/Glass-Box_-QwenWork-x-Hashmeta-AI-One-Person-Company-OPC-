-- Glass-Box Governance Gateway: Ontology Schema (SQLite, deterministic)
-- Design rule: NO LLM in this layer. Every decision below is a set-membership /
-- max-rank computation over explicit graph relationships. Same input => same verdict, always.

-- Layer 1: Policy & Sensitivity Ontology -------------------------------------
-- AvePoint's four sensitivity tiers, ranked so "most restrictive wins" is a MAX.
CREATE TABLE sensitivity_tier (
  key         TEXT PRIMARY KEY,          -- public | internal | client_confidential | regulated
  rank        INTEGER NOT NULL UNIQUE,   -- 0 | 1 | 2 | 3
  label       TEXT NOT NULL,
  definition  TEXT NOT NULL
);

-- Action classes the worker agent can request.
CREATE TABLE action_class (
  key           TEXT PRIMARY KEY,        -- e.g. external_email
  label         TEXT NOT NULL,
  blast_radius  TEXT NOT NULL            -- local | org | external_side_effect | irreversible
);

-- The policy matrix: (tier, action) -> decision. Exhaustive by construction:
-- the gate ERRORS on any missing cell, so no edge case can silently fall through.
CREATE TABLE policy_rule (
  tier_key   TEXT NOT NULL REFERENCES sensitivity_tier(key),
  action_key TEXT NOT NULL REFERENCES action_class(key),
  decision   TEXT NOT NULL CHECK (decision IN ('ALLOW','REQUIRE_OWNER','HARD_BLOCK')),
  rule_text  TEXT NOT NULL,              -- human-readable citation for the console
  PRIMARY KEY (tier_key, action_key)
);

-- Layer 2: Verified Ground-Truth Knowledge Graph ------------------------------
-- One lean node/edge pair (no Neo4j/OWL). Multi-hop tier inheritance + provenance.
CREATE TABLE node (
  id         TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  type       TEXT NOT NULL,              -- document|record|tender|ledger_entry|benchmark|contact|vendor|draft
  tier       TEXT REFERENCES sensitivity_tier(key),  -- NULL for pure entity nodes
  props      TEXT NOT NULL DEFAULT '{}'  -- JSON: uen, email, period, etc.
);

CREATE TABLE edge (
  src  TEXT NOT NULL REFERENCES node(id),
  rel  TEXT NOT NULL,                    -- references|contains|pertains_to|sent_to|classified_as
  dst  TEXT NOT NULL REFERENCES node(id),
  PRIMARY KEY (src, rel, dst)
);

-- Numeric ground truth: every fact carries value + provenance (source_uri, as_of_date).
CREATE TABLE fact (
  entity     TEXT NOT NULL REFERENCES node(id),  -- resolved by name/UEN at check time
  measure    TEXT NOT NULL,              -- revenue | tender_award_value | benchmark_pct | invoice_total ...
  value      REAL NOT NULL,
  unit       TEXT NOT NULL,              -- SGD | PCT | COUNT
  period     TEXT,
  source_uri TEXT NOT NULL,              -- data.gov.sg / GeBIZ / internal ledger reference
  as_of_date TEXT NOT NULL,
  PRIMARY KEY (entity, measure)
);

-- Recipient authorization: what tier each known external party may receive,
-- and (for client contacts) which client they belong to. Deterministic ceiling check.
CREATE TABLE recipient (
  node_id          TEXT PRIMARY KEY REFERENCES node(id),
  email            TEXT NOT NULL UNIQUE, -- cross-check against node.props.email
  tier_ceiling     INTEGER NOT NULL,     -- max tier rank this party may receive
  owner_client_id  TEXT                  -- if set, only that client's confidential docs pass
);
-- Fail-closed invariant: an email with NO row here is an unknown party;
-- the gate treats unknown recipients as ceiling = -1 (hard block), never as public.

-- Audit / interception log (the console and the morning digest read this).
CREATE TABLE interception_log (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  ts            TEXT NOT NULL,
  draft_id      TEXT NOT NULL,
  action_key    TEXT NOT NULL,
  decision      TEXT NOT NULL,            -- ALLOW | REQUIRE_OWNER | HARD_BLOCK
  rule_path     TEXT NOT NULL,            -- exact ontology traversal, e.g. "Entity(d1)-classified_as->regulated x external_email => HARD_BLOCK"
  facts_checked  INTEGER NOT NULL DEFAULT 0,
  facts_flagged  INTEGER NOT NULL DEFAULT 0,
  evidence       TEXT NOT NULL DEFAULT '[]',  -- JSON array of contradiction cards
  owner_status   TEXT                          -- NULL | approved:<ts> | rejected:<ts>
);
