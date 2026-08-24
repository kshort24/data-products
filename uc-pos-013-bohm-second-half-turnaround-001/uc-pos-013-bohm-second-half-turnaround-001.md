# Use Case Contract — uc-pos-013-bohm-second-half-turnaround-001

| Field | Value |
|---|---|
| UC ordinal | **38** |
| use_case_id | `uc-pos-013-bohm-second-half-turnaround-001` |
| build_id | `dp_uc37` |
| Value stream | Phillies Offense (`pos`) |
| Subject | Alec Bohm — MLBAM **664761** (confirmed by filter), RHB, PHI 2020–2026 |
| Requester / DPO | Kellen Short |
| Submitted | 2026-08-23 · Delivered **2026-08-24** |
| Variant | Second-half turnaround audit (mirror of the `-first-half-allstar` family; first pos-side post-break retrospective) |
| Data window | 2015 → 2026-08-22 (freshness T-1 at build; season live) |
| Status | **Delivered — certification ready — publish approved (internal)** |

## Use case (as submitted)

Assess whether Alec Bohm has genuinely turned his season around since the All-Star break, calibrating
that the outcomes are positive before explaining them. Top-line KPIs: **SLG, BA with RISP, run
creation**, plus DPO-delegated additions. Underlying: contact quality — **pull-air** (prior DPO
digging), hard-hit, air, barrel; swing decisions — the "rarely whiffs" identity and any approach
change. Other angles: platoon splits and pitch groups. Identify whether specific actions by personas
in the Phillies Offense value stream could have driven the outcomes. A working notebook snippet
supplied the break operator, level, KPI list, display-name dictionary, required governed functions,
and a merge-chain method (two paren transpositions repaired at intake, logged — C-5).

## Acceptance criteria → outcome

| Criterion | Outcome |
|---|---|
| Premises tested before mechanisms, one verdict table | ✅ report §1 (6 verdicts: TRUE ×3, TRUE-with-flag, FALSE-on-volume/TRUE-on-quality, MOSTLY FALSE) |
| All three named top-line KPIs at the break grain | ✅ SLG .351→.488 · BA w/RISP .299→.462 (42 PA ⚠) · RC .130→.207 per PA |
| Pull-air answered despite O-7 | ✅ remediated (PA-L1/PA-F1, provisional); volume flat/14th pctile, quality spiked |
| Whiff/approach answered against a population benchmark | ✅ 218-season pool; post z-whiff ~2nd pctile; approach unchanged |
| Platoon + pitch-group splits with floors enforced | ✅ PL-1 mix effect −18 wOBA pts; breaking-ball fix headline; sub-floor cells ⚠ everywhere |
| Persona actionability without causal overreach | ✅ report §5 hypothesis table, causation disclaimed |
| Outcome-selected window priced both ways | ✅ 10-point scan; sign survives all boundaries |
| Full governed package: 00–07, receipts, verification, PDF, dashboard | ✅ this folder · 227/227 PASS |

## Manual carry-ins (not in the data plane)

All-Star break calendar facts (no PHI games 13–15 Jul 2026 — verified empty in-plane); "middle of the
lineup" role (batting-order slot not a column — scoped out, C-4); any coaching/medical interventions
(§5 hypotheses only).

## Freshness manifest

`phils_2015..2026.parquet` loaded (12/12); max `game_date` 2026-08-22; `wOBA and FIP Constants.csv`
seasons 2015–2026 present; `Baseball Functions.ipynb` authority re-checked at intake (cell 24 still
reads `loc_*` — O-7 confirmed live before remediation).

## Ledger

Row appended via `uc_ledger_AI_PATCH_uc-pos-013-bohm.md` (MLB repo root, pending paste).
**Next available after this UC: UC #39 / dp_uc38 (pps next uc-pps-027 · pos next uc-pos-014).**
