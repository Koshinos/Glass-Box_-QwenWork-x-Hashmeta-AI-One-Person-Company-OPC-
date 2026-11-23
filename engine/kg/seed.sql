-- Glass-Box Governance Gateway: Seed Data
-- Tier ranks encode AvePoint's four sensitivity labels. MAX(rank) = most restrictive.
INSERT INTO sensitivity_tier VALUES
  ('public',              0, 'Public',              'Publishable SG public records (ACRA, GeBIZ,SingStat).'),
  ('internal',            1, 'Internal',            'Firm working data: pipelines, benchmarks, ledgers.'),
  ('client_confidential', 2, 'Client-Confidential', 'Named-client commercial data: invoices, contracts, bids.'),
  ('regulated',           3, 'Regulated',           'PDPA personal data / statutory records. Highest restriction.');

INSERT INTO action_class VALUES
  ('read_summarize_local', 'Read/summarize locally',        'local'),
  ('internal_system_write','Write to firm systems',         'org'),
  ('third_party_upload',   'Upload to third-party service', 'external_side_effect'),
  ('external_email',       'Send email outside the firm',   'external_side_effect'),
  ('public_post',          'Publish to a public channel',   'external_side_effect'),
  ('execute_payment',      'Initiate a money movement',     'irreversible'),
  ('sign_contract',        'Execute a binding signature',   'irreversible');

-- Policy matrix, all 28 cells populated (the gate errors on any missing cell => no silent fall-through).
INSERT INTO policy_rule VALUES
  ('public','read_summarize_local','ALLOW','Public records may be processed locally without sign-off.'),
  ('public','internal_system_write','ALLOW','Public records may enter firm systems.'),
  ('public','third_party_upload','ALLOW','Public records carry no confidentiality obligation.'),
  ('public','external_email','ALLOW','Public records may be emailed; fact-check still applies.'),
  ('public','public_post','ALLOW','Public records may be published; fact-check still applies.'),
  ('public','execute_payment','REQUIRE_OWNER','All money movements require founder sign-off.'),
  ('public','sign_contract','REQUIRE_OWNER','All signatures require founder sign-off.'),
  ('internal','read_summarize_local','ALLOW','Internal data may be read and summarized.'),
  ('internal','internal_system_write','ALLOW','Internal data may stay within firm systems.'),
  ('internal','third_party_upload','REQUIRE_OWNER','Internal data leaves the firm only with owner OK.'),
  ('internal','external_email','REQUIRE_OWNER','Internal data has no autonomous external channel.'),
  ('internal','public_post','HARD_BLOCK','Internal working data is never published autonomously.'),
  ('internal','execute_payment','REQUIRE_OWNER','All money movements require founder sign-off.'),
  ('internal','sign_contract','REQUIRE_OWNER','All signatures require founder sign-off.'),
  ('client_confidential','read_summarize_local','ALLOW','Confidential data may be read/summarized in-scope.'),
  ('client_confidential','internal_system_write','ALLOW','Confidential data may stay within firm systems.'),
  ('client_confidential','third_party_upload','HARD_BLOCK','No third-party processors for client-confidential data.'),
  ('client_confidential','external_email','REQUIRE_OWNER','Downgrades to ALLOW only via Authorized-Recipient Exception (fail-closed: unknown recipient => HARD_BLOCK).'),
  ('client_confidential','public_post','HARD_BLOCK','Client-confidential data is never published.'),
  ('client_confidential','execute_payment','HARD_BLOCK','Client funds/trust movements are owner-executed only.'),
  ('client_confidential','sign_contract','HARD_BLOCK','Agent can never bind the client or the firm.'),
  ('regulated','read_summarize_local','ALLOW','PDPA records may be summarized within purpose scope.'),
  ('regulated','internal_system_write','REQUIRE_OWNER','Any write of regulated records needs owner OK.'),
  ('regulated','third_party_upload','HARD_BLOCK','No self-service channel for regulated records.'),
  ('regulated','external_email','HARD_BLOCK','PDPA purpose-bound send is not agent-delegable. No exceptions.'),
  ('regulated','public_post','HARD_BLOCK','Regulated records are never published.'),
  ('regulated','execute_payment','HARD_BLOCK','Statutory-fund movements are owner-executed only.'),
  ('regulated','sign_contract','HARD_BLOCK','Regulated-signature flows are owner-executed only.');

-- ---------------------------------------------------------------------------
-- Ground-truth graph. Entities are fictitious demo OPC clients in REAL SG formats
-- (UEN 8-digit+check / ACRA style; GeBIZ award shape; SingStat PPI shape).
-- source_uri 'demo://' rows are replaced with live data.gov.sg / GeBIZ records by
-- the VM bootstrap fetcher on the Agent Computer (see QWENWORK_SETUP.md).
INSERT INTO node VALUES
  ('client:azure',   'Azure Bay Retail Pte. Ltd.',   'client','internal','{"uen":"201824567W"}'),
  ('client:merlion', 'Merlion Logistics Pte. Ltd.',  'client','internal','{"uen":"201611223M"}'),
  ('vendor:nusa',    'Nusa Payments Pte. Ltd.',      'vendor','public','{"uen":"202034567E"}'),
  ('contact:sarah',  'Sarah Chen (Azure Ops Lead)',  'contact','client_confidential','{"email":"sarah.chen@azurebay.example","client":"client:azure","ceiling":2}'),
  ('contact:rafael', 'Tan Wei Jun (Merlion CFO)',    'contact','client_confidential','{"email":"rafael.tan@merlionlogistics.example","client":"client:merlion","ceiling":2}'),
  ('contact:lim',    ' LIM & Co External Advisory',  'contact','internal','{"email":"advisory@limco.example","ceiling":1}'),
  ('rec:payroll_feb26','PDPA payroll export Feb 2026','record','regulated','{"headcount":47}'),
  ('rec:inv_az_041', 'Invoice INV-2026-041 (Azure)',  'ledger_entry','client_confidential','{"invoice":"INV-2026-041"}'),
  ('rec:contract_amend','Azure MSA Amendment 2026',   'document','client_confidential','{}'),
  ('rec:gebiz_1187', 'GeBIZ TA-2025-1187 analytics award','tender','public','{"winner":"client:merlion"}'),
  ('rec:sgstat_ppi', 'SingStat PPI Prof. Services Q4 FY2025','benchmark','internal','{}');

INSERT INTO edge VALUES
  ('client:azure','contains','rec:inv_az_041'),
  ('client:azure','contains','rec:contract_amend'),
  ('client:merlion','contains','rec:gebiz_1187'),
  ('rec:contract_amend','references','rec:inv_az_041'),
  ('rec:sgstat_ppi','pertains_to','client:azure');

-- Every fact: value + provenance. These are the ONLY numbers the Fact Gate trusts.
INSERT INTO fact VALUES
  ('client:azure','revenue',        8500000,  'SGD','FY2025','demo://internal-ledger/azure-bay/fy2025','2026-01-31'),
  ('client:azure','invoice_total',     86400,  'SGD','INV-2026-041','demo://internal-ledger/invoice/INV-2026-041','2026-02-10'),
  ('client:merlion','tender_award_value',412000,'SGD','TA-2025-1187','demo://gebiz/awards/TA-2025-1187','2025-09-12'),
  ('client:azure','benchmark_pct',      2.1,   'PCT','Q4 FY2025','demo://singstat/ppi/prof-services/2025Q4','2026-03-01');

INSERT INTO recipient VALUES
  ('contact:sarah',  'sarah.chen@azurebay.example',          2, 'client:azure'),
  ('contact:rafael', 'rafael.tan@merlionlogistics.example',  2, 'client:merlion'),
  ('contact:lim',    'advisory@limco.example',               1, NULL);
-- vendor:nusa has NO recipient row => unknown party => fail-closed ceiling -1.
