# 00 — DPO Delivery Spine · uc-pos-004 (dp_uc20) · Kyle Schwarber First-Half 2026

**Use case:** First-half 2026 retrospective on Kyle Schwarber (2026 NL All-Star, Home Run Derby runner-up): high-level measurables, a user-specified KPI panel (HR, run creation, wOBA, SLG, OPS, OBP, BA, hard-hit, barrel, P/PA) on top of the standard scouting set, and a quantified read on the *approach* driving those outcomes.
**Requested by / DPO:** Kellen Short, 2026-07-14 · **Depth:** full governance package + token-telemetry pilot (DPO-confirmed at intake) · **Deliverable:** branded PDF report + receipts + trail + telemetry ledger.

## Sequencing & numbering decision (ledger note — ACTION FOR KELLEN)
- Repo verification (`ls dp_uc*`, `ls uc-*`, control-plane `data-products/`) shows deliveries through **dp_uc19** (Duran, contract uc-pps-018, UC ordinal #20) and pos contracts through **uc-pos-003** (control plane).
- Claimed: **UC ordinal #21 · contract id `uc-pos-004` · build prefix `dp_uc20`.** No collision with any root file, `out/` receipt, or control-plane folder.
- **Ledger needs this row appended** and "Next available" bumped to UC #22 / dp_uc21 (pps next: uc-pps-019; pos next: uc-pos-005).

## Layer sequencing (all gates passed in order)
| Layer | Agent role | Artifact | Status |
|---|---|---|---|
| 1 Intake | use-case-validator | 01 | PASS (3 non-blocking gaps, resolved by DPO decision) |
| 1 Intake | source-system-profiler | 02 | PASS (full-career coverage confirmed; entity lock 656941) |
| 1 Intake | business-glossary | 03 | PASS (2 new terms: SC-1 wRC, SC-2 P/PA — provisional) |
| 2 Design | data-architect + kpi-calculator | 04 / 03 | PASS (grain locked; kernel inherited verbatim from dp_uc18; 2 new KPI specs) |
| 3 Build | data-engineer | `dp_uc20_schwarber_first_half.py` | PASS (run 2026-07-14; 17 CSV + 3 PNG receipts + buildlog) |
| 3 Build | data-quality-engineer | 05 + `out/dp_uc20_*_dq_receipts.csv` | PASS structural checks |
| 4 Certify | certification-agent + verification | 06 + `dp_uc20_verification.py` | READY — **18/18 independent recompute PASS** |
| 4 Publish | consumption docs + observability | 07 | Delivered |
| — Pilot | token-economist (proposed) | `../…/telemetry/` + agent def | First telemetry ledger captured on this run |

## Governance guardrails honored
1. No CDE inference — locked dp_uc18 kernel inherited verbatim; the two NEW KPIs (wRC, P/PA) carry full kpi-calculator specs in 03 and are flagged provisional pending glossary approval.
2. No build without specs — build script implements 04's model/lineage only.
3. No publish without certification — 06 returned READY (backed by 18/18 verification) before the PDF was presented.
4. **All-Star selection and Derby runner-up are manual carry-ins** (DPO-provided at intake, 2026-07-14): neither is derivable from the pitch log. They appear only as carried-in facts in the report header, never in a computed table.
5. Privacy: public MLB performance data, no PII beyond public player identity — privacy-watchdog pass trivial, noted in 06. Bio measurables (age, height, weight) are labeled reference carry-ins.

## Escalations to human DPO
- Depth tier + token-economist scope → full package + agent def + pilot telemetry (answered 2026-07-14).
- Ledger update (above) → open.
- SC-1 / SC-2 glossary promotion from provisional → open (recommend approve; formulas are FanGraphs-standard).
