# 00 — DPO Delivery Spine · uc-pps-018 (dp_uc19) · Jhoan Duran First-Half 2026

**Use case:** First-half 2026 retrospective on Jhoan Duran (Phillies closer, 2026 NL All-Star): what were the results, has he done anything differently to start this year, and is the improvement over his 2025 Phillies stint and Twins career real?
**Requested by / DPO:** Kellen Short, 2026-07-13 · **Depth:** full governance package (DPO-confirmed at intake) · **Deliverable:** branded PDF report + receipts + trail.

## Sequencing & numbering decision (ledger note — ACTION FOR KELLEN)
- Skill-side ledger says "next: UC #12" — stale. Repo verification (`ls dp_uc*`, `ls uc-*`) shows deliveries through **dp_uc18** (Marsh) and contracts through **uc-pps-017** (Luzardo ASG, 2026-07-13, artifacts pending paste).
- Claimed: **UC ordinal #20 · contract id `uc-pps-018` · build prefix `dp_uc19`** (19 is the lowest unclaimed prefix: 17 = Luzardo per its contract, 18 = Marsh). No collision with any root file, `out/` receipt, or pending-paste artifact.
- **Ledger needs two rows appended** (uc-pps-017/dp_uc17 Luzardo; uc-pps-018/dp_uc19 Duran) and "Next available" bumped to UC #21 / uc-pps-019 / dp_uc20.

## Layer sequencing (all gates passed in order)
| Layer | Agent role | Artifact | Status |
|---|---|---|---|
| 1 Intake | use-case-validator | 01 | PASS (2 non-blocking gaps, resolved by DPO decision) |
| 1 Intake | source-system-profiler | 02 | PASS (fitness confirmed, seam verified) |
| 1 Intake | business-glossary | 03 | PASS (no new terms needed) |
| 2 Design | data-architect + kpi-calculator | 04 / 03 | PASS (grain locked; KPIs inherited verbatim, none new) |
| 3 Build | data-engineer | `dp_uc19_duran_first_half.py` | PASS (run 2026-07-13; 8 CSV + 3 PNG receipts) |
| 3 Build | data-quality-engineer | 05 + `out/dp_uc19_dq_scorecard.csv` | PASS 5/5 structural checks |
| 4 Certify | certification-agent | 06 | READY |
| 4 Publish | consumption docs + observability | 07 | Delivered |

## Governance guardrails honored
1. No CDE inference — all metrics from the locked dp_uc11 kernel; no new business meanings defined.
2. No build without specs — build script implements 04's model/lineage only.
3. No publish without certification — 06 returned READY before the PDF was presented.
4. **Saves are a manual carry-in** (DPO decision at intake, 2026-07-13): pitch-level Statcast has no official save flag; DPO elected NOT to derive one. 24 saves appear only as a carried-in fact in the freshness manifest and report, never in a computed table.
5. Privacy: public MLB performance data, no PII beyond public player identity — privacy-watchdog pass trivial, noted in 06.

## Escalations to human DPO
- Depth tier → full package (answered 2026-07-13).
- Saves derivation vs carry-in → carry-in (answered 2026-07-13).
- Ledger update (above) → open.
