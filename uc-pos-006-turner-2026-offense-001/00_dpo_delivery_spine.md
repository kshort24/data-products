# 00 — DPO Delivery Spine · uc-pos-006 (dp_uc24) · Trea Turner 2026 Offense

**Use case:** 2026 offensive retrospective on Trea Turner — high-level results against his full career (WSN → LAD → PHI), a diagnosis of *why* the results are down through the underlying batted-ball and swing-decision indicators (barrel, hard-hit, pulled-air, line-drive, chase/whiff, pitch-group), a read on the recent "heating up," and persona actions (Turner, manager, hitting staff). Signature deliverable: a cumulative season-to-date OPS trajectory, 2026 highlighted against prior-year shadows.
**Requested by / DPO:** Kellen Short, 2026-07-21 · **Depth:** full governance package + interactive HTML explorer + one-page persona action card (DPO-confirmed at intake) · **Deliverable:** branded PDF report + receipts + governance trail + two consumables.

## Sequencing & numbering decision (ledger note — ACTION FOR KELLEN)
- Repo verification (`ls dp_uc*`, `ls uc-*`, control-plane `data-products/`) and `uc_ledger_AI.md` header confirm **Next available: UC #25 / dp_uc24 (pos next: uc-pos-006)** as of 2026-07-15.
- Claimed: **UC ordinal #25 · contract id `uc-pos-006` · build prefix `dp_uc24`.** No collision with any root file, `out/` receipt, or control-plane folder (verified: `dp_uc24` / `uc-pos-006` free).
- **Ledger needs this row appended** and "Next available" bumped to UC #26 / dp_uc25 (pps next: uc-pps-021; pos next: uc-pos-007). Ready-to-paste row: `uc_ledger_AI_PATCH_uc-pos-006-turner.md` (MLB repo root). Per the new-files-only rule the ledger was NOT edited in place.

## Layer sequencing (all gates passed in order)
| Layer | Agent role | Artifact | Status |
|---|---|---|---|
| 1 Intake | use-case-validator | 01 | PASS (4 non-blocking gaps, resolved by DPO decision) |
| 1 Intake | source-system-profiler | 02 | PASS (full-career coverage; entity lock 607208; fresh through 2026-07-20) |
| 1 Intake | business-glossary | 03 | PASS (2 new terms: RF-1 trajectory, RF-2 rolling form — provisional) |
| 2 Design | data-architect + kpi-calculator | 04 / 03 | PASS (grain locked; kernel inherited verbatim from dp_uc20; 2 new KPI specs) |
| 3 Build | data-engineer | `dp_uc24_turner_2026_review.py` | PASS (run 2026-07-21; 16 CSV + 5 PNG receipts) |
| 3 Build | data-quality-engineer | 05 + `out/dp_uc24_*_dq_receipts.csv` | PASS (0 dup keys; BIP null ≤0.94%) |
| 4 Certify | certification-agent + verification | 06 + `dp_uc24_verification.py` | READY — **33/33 independent recompute PASS** |
| 4 Publish | analytics-enabler + consumer-onboarding + observability | 07 | Delivered (+ interactive HTML, persona card) |

## Governance guardrails honored
1. **No CDE inference** — locked dp_uc20 / dp_uc18 kernel inherited verbatim; the two NEW KPIs (RF-1, RF-2) carry full kpi-calculator specs in 03 and are flagged provisional pending glossary approval; SC-1/SC-2 inherited from uc-pos-004.
2. **No build without specs** — build script implements 04's model/lineage only.
3. **No publish without certification** — 06 returned READY (backed by 33/33 verification) before the PDF was presented.
4. **Honesty gate enforced by verification** — an initial "career-low pulled-air / pull rate" claim was **caught and corrected to "Phillies-era low, lowest since 2020"** when the recompute showed 2020 was lower (.111 vs .117). Logged in 05.
5. **Manual carry-ins** — 2026 All-Star break date (07-16) and roster/health context are DPO-provided, not derivable from the pitch log; they appear only as carried-in facts, never in a computed table.
6. **Privacy** — public MLB performance data, no PII beyond public player identity; privacy-watchdog pass trivial, noted in 06.

## Escalations to human DPO
- Depth tier + extra consumables → full package + interactive HTML + persona card (answered 2026-07-21).
- Ledger update (above) → open.
- RF-1 / RF-2 glossary promotion from provisional → open (recommend approve after one more hitter reuse).
- Post-run backtest (August EV top-end re-check; does the July recovery hold past 62 PA?) → offered as closure step (07).
