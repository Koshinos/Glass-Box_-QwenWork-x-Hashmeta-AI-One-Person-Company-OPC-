-- 10 Singapore B2B consultancy records. Entities are FICTIONAL but use real
-- ACRA / GeBIZ / NRIC formats. Live data.gov.sg + GeBIZ values replace these
-- via the VM bootstrap (see QWENWORK_SETUP.md Step 1); no real company is
-- attributed a fake number here.
BEGIN;

DELETE FROM kg_edges; DELETE FROM policy_rules; DELETE FROM kg_nodes;

-- ---- Promise layer (merged from the PromiseCascade idea) ------------------
-- Offer = the thing promises attach to. Terms are VERSIONED rule nodes:
-- each carries effective_date/expires_date; only one version is current.
-- Agreements freeze the rule values at signature date => vintage exemption.
INSERT INTO kg_nodes (id,name,type,tier,props) VALUES
 ('offer:core','Core Service Retainer — standard terms v1','offer','internal','{"version":1,"measure":"offer_price","value":1200,"unit":"SGD","effective_date":"2025-11-01","expires_date":"2026-11-19","sla_days":7,"source_uri":"internal://terms/core-v1","as_of_date":"2025-11-01"}'),
 ('offer:core-v2','Core Service Retainer — standard terms v2','offer','internal','{"version":2,"measure":"offer_price","value":1500,"unit":"SGD","effective_date":"2026-11-20","expires_date":null,"sla_days":14,"source_uri":"internal://terms/core-v2","as_of_date":"2026-11-20"}'),
 ('agr:nexgate','Signed MSA — Nexgate Pte Ltd (fixed price + SLA)','agreement','client_confidential','{"measure":"offer_price","value":1200,"unit":"SGD","effective_date":"2025-12-01","expires_date":null,"sla_days":7,"client":"client:nexgate","signed_date":"2025-12-01","recipients":["wei.lim@nexgate.example"],"source_uri":"internal://agreements/nexgate-msa","as_of_date":"2025-12-01"}'),
 ('client:nexgate','Nexgate Pte. Ltd. (ACRA UEN 201933221K)','client','public','{"uen":"201933221K","source_uri":"https://www.acra.gov.sg","as_of_date":"2026-02-01"}'),
 ('asset:pricing_page','Hashmeta site — pricing page','content_asset','public','{"measure":"offer_price","value":1200,"unit":"SGD","effective_date":"2026-11-22","expires_date":null,"sla_days":7,"source_uri":"https://glassbox.geo.hashmeta.tech/pricing","as_of_date":"2026-11-22"}');

INSERT INTO kg_nodes (id,name,type,tier,props) VALUES
-- 4 VERIFIED PUBLIC (ACRA UENs + GeBIZ award values)
 ('pub:acra_sensocore','SensoCore Analytics Pte. Ltd. (ACRA UEN 201812345M)','client','public',
  '{"uen":"201812345M","source_uri":"https://www.acra.gov.sg","as_of_date":"2026-02-01","facts":{"paid_up_capital":250000},"authorized_recipients":[{"email":"sarah.chen@sensocore.example","owner":"pub:acra_sensocore","ceiling":2}]}'),
 ('pub:acra_mariserv','MariServ Consultancy Pte. Ltd. (ACRA UEN 202098765K)','client','public',
  '{"uen":"202098765K","source_uri":"https://www.acra.gov.sg","as_of_date":"2026-02-01","facts":{"paid_up_capital":120000},"authorized_recipients":[{"email":"wei.jun@mariserv.example","owner":"pub:acra_mariserv","ceiling":2}]}'),
 ('pub:gebiz_2025_1187','GeBIZ Award TA-2025-1187 — Cloud Migration Advisory','tender','public',
  '{"source_uri":"https://www.gebiz.gov.sg","as_of_date":"2025-09-12","facts":{"tender_award_value":412000}}'),
 ('pub:gebiz_2025_0904','GeBIZ Award TA-2025-0904 — Data Governance Framework','tender','public',
  '{"source_uri":"https://www.gebiz.gov.sg","as_of_date":"2025-06-30","facts":{"tender_award_value":188500}}'),

-- 2 INTERNAL SOPs
 ('int:sop_outreach','Internal SOP: Client Outreach & Proposal Template','sop','internal','{"owner":"firm","version":"4.2"}'),
 ('int:sop_billing','Internal SOP: Billing & Collections Cycle','sop','internal','{"owner":"firm","version":"1.9"}'),

-- 2 CLIENT-CONFIDENTIAL PROPOSALS
 ('conf:proposal_nusagov','NusaGov Digital Roadmap (Client-Confidential Proposal)','proposal','client_confidential',
  '{"client":"pub:acra_sensocore","source_uri":"internal://proposals/nusagov-2026","as_of_date":"2026-01-20","facts":{"proposed_fee":640000,"firm_annual_revenue":850000}}'),
 ('conf:proposal_retailops','RetailOps Turnaround (Client-Confidential Proposal)','proposal','client_confidential',
  '{"client":"pub:acra_mariserv","source_uri":"internal://proposals/retailops-2026","as_of_date":"2026-01-28","facts":{"proposed_fee":375000}}'),

-- 2 REGULATED payroll / NRIC records
 ('reg:payroll_feb','Regulated: Payroll Register Feb 2026','record','regulated',
  '{"pdpa":1,"facts":{"payroll_total":214300},"headcount":47}'),
 ('reg:nric_register','Regulated: NRIC/FIN Master Register (PDPA)','record','regulated',
  '{"pdpa":1,"sample_nric":"S6801234D","facts":{"nric_records":312}}');

-- Graph edges: which ground-truth nodes each artefact relies on. The Policy
-- Gate walks these to compute a document's EFFECTIVE tier (max-rank, hop-capped).
INSERT INTO kg_edges VALUES
 ('conf:proposal_nusagov','references','pub:acra_sensocore'),
 ('conf:proposal_nusagov','references','pub:gebiz_2025_1187'),
 ('conf:proposal_retailops','references','pub:acra_mariserv'),
 ('conf:proposal_retailops','references','pub:gebiz_2025_0904'),
 ('int:sop_outreach','references','conf:proposal_nusagov'),
 ('reg:payroll_feb','pertains_to','pub:acra_sensocore'),
 ('reg:nric_register','pertains_to','pub:acra_mariserv'),
 -- promise-layer structure (deliberately NOT in references/contains so they
 -- never inflate a document's tier; Promise Gate uses its own rel vocabulary)
 ('offer:core-v2','succeeds','offer:core'),
 ('agr:nexgate','is_exception_to','offer:core'),
 ('agr:nexgate','scoped_to','client:nexgate'),
 ('asset:pricing_page','asserts','offer:core');

-- ---- POLICY RULES -------------------------------------------------------------
-- Tier ranks: public 0, internal 1, client_confidential 2, regulated 3.
-- Requirement quotes from the brief:
--   * send_external_email OR export_csv on client-confidential => REQUIRE_OWNER
--   * anything touching regulated                              => HARD_BLOCK
INSERT INTO policy_rules (tier,action,decision,rule_text) VALUES
 ('client_confidential','send_external_email','REQUIRE_OWNER','Confidential proposal may leave the firm only with founder sign-off (authorized-recipient exception applies; unknown recipient => HARD_BLOCK).'),
 ('client_confidential','export_csv','REQUIRE_OWNER','Bulk CSV export of client-confidential data requires founder sign-off.'),
 ('client_confidential','public_post','HARD_BLOCK','Confidential data is never published.'),
 ('client_confidential','execute_payment','HARD_BLOCK','Agent cannot move client funds.'),
 ('client_confidential','sign_contract','HARD_BLOCK','Agent cannot bind the client or the firm.'),
 ('client_confidential','third_party_upload','HARD_BLOCK','No third-party processors for client-confidential data.'),
 ('client_confidential','read_summarize_local','ALLOW','Reading/summarizing confidential data in-scope is fine.'),

 -- "anything touching regulated => HARD_BLOCK": the wildcard action * covers
 -- every action class, including ones added later. read stays blocked because
 -- reads of PDPA records are themselves the exfil primitive we must stop.
 ('regulated','*','HARD_BLOCK','PDPA / statutory records: no agent-delegable action. No exceptions.'),

 ('internal','send_external_email','REQUIRE_OWNER','Internal SOP has no autonomous external channel.'),
 ('internal','export_csv','ALLOW','Firm working data may be exported internally.'),
 ('internal','public_post','HARD_BLOCK','Internal working data is never published autonomously.'),
 ('internal','execute_payment','REQUIRE_OWNER','All money movements need founder sign-off.'),
 ('internal','read_summarize_local','ALLOW','Internal data may be read and summarized.'),

 ('public','*','ALLOW','Public ACRA/GeBIZ records carry no confidentiality obligation; fact-checking still applies.'),
 ('public','execute_payment','REQUIRE_OWNER','All money movements need founder sign-off even if the record is public.'),
 ('public','sign_contract','REQUIRE_OWNER','Signatures need founder sign-off even if the record is public.');

COMMIT;
