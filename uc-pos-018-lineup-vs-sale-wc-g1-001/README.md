# The Phillies lineup vs Chris Sale: NLWCS Game 1

**UC #50 · `uc-pos-018` · `dp_uc50` · v1.0.0 · delivered 2026-09-29 (pre-game) · READY-CONDITIONAL · independently verified (372/372)**
Position player / offense (`pos`) · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| the one page for the dugout | `out/dp_uc50_fig4_lineup_notecard.png` (MLB root) |
| a hitter's card | `out/dp_uc50_card_{1..9}_{name}.png` |
| the whole scout on paper | `dp_uc50_lineup_vs_sale_report.pdf` (MLB root, 15 pp) |
| Sale, 2026 | report §1, `out/dp_uc50_fig2_sale_arsenal.png`, `out/dp_uc50_fig3_sale_tto.png` |
| which of your notebook claims held | report §5, `03` §6, `out/dp_uc50_hp_reconciliation.csv` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_…md` → `07` §3 |

## The finding, in one paragraph

Sale's 2026 was the same as his 2024 (.258 wOBA against in 650 PA, 30.8% K, 4.8% BB) with 1.3 more mph on the four-seam (96.1). The lefties at the top of the order can't be the plan: Schwarber and Harper are a combined 1-for-23 against him this year (.066 wOBA), and Harper's .190 career OPS makes Sale the toughest of the 20 lefties he's seen 20+ times. The right side has done the work (.278 wOBA career in 111 PA). Bohm is the best bet on the card (.365 in 25 PA, and at least .345 against lefties in every season he's played). Sale doesn't fade the third time through (.262 / .254 / .258). Every card's plan is the same rule in that hitter's terms: **make the slider a ball and the four-seam a strike.**

## The nine cards

| # | Hitter | Tag |
|---|---|---|
| 1 | Trea Turner (R) | Unlucky against lefties, and the soft stuff is the leak |
| 2 | Kyle Schwarber (L) | Career damage, 2026 silence |
| 3 | Bryce Harper (L) | The one pitcher he hasn't solved |
| 4 | Alec Bohm (R) | The matchup bat: contact that Sale hasn't beaten |
| 5 | Derek Hill (R) | Fastball or nothing |
| 6 | Bryan De La Cruz (R) | The slider test |
| 7 | Bryson Stott (L) | A results rebound without the damage |
| 8 | Edmundo Sosa (R) | A lefty masher Sale has figured out |
| 9 | J.T. Realmuto (R) | Hitting it at people, not over them |

## Package contents

```
00_dpo_orchestration_record.md   the spine: framing, 10 gates, capability table, arguments, 7 escalations, C1–C5
01_strategy_intake.md            ID reservation, 6 gaps, id-scan source profile, coverage, carry-ins, glossary deltas
02_engineering_design.md         BF-1 one-frame model, 10 EDA findings, joins, metadata map, card/notecard spec
03_governance.md                 Rule-1 search, KPI specs (XW-1 HL-1 LR-1 TT-1 IC-1 NF-2 BF-1), lineage, defects, HP grading, versioning
04_engineering_build.md          manifest + hashes, parent pins, environment, build-time assertions, receipts, reproduce
05_quality_certification.md      DQ 15/2/0, render QA, harness 372/372, what the harness caught, readiness
06_consumer_success.md           forms and readers, reading paths, persona notes, FAQ, catalog entry
07_platform_marketing.md         tripwires, cost audit, bid vs actual, calibration, what's next
BID_2026-09-29_…md               the competitive bid: filed, awarded, reconciled in 07 (D-1 disclosed)
uc-pos-018-Phillies Lineup vs Chris Sale 20260929.md   repo-side contract (copy; the original is at the MLB root)
uc_ledger_AI_PATCH_uc-pos-018-lineup-vs-sale.md        PENDING PASTE
code/                            copies of the dp_uc50 scripts as delivered (the MLB root copies are canonical)
```

**Data plane (MLB repo root):** `dp_uc50_kernel.py` · `dp_uc50_lineup_vs_sale.py` · `dp_uc50_narratives.py` · `dp_uc50_build_figs.py` · `dp_uc50_build_report.py` · `dp_uc50_build_pdf.py` · `dp_uc50_verification.py` · `dp_uc50_lineup_vs_sale_report.md/.pdf` · `out/dp_uc50_*`.

## Governed objects: inherited vs introduced

**Inherited by import (sha256-pinned):** `dp_uc44_kernel` (nresults, whiff, chase, pitch_mix, bb_type, hard-hit, two_prop_z) · `dp_uc46_kernel` (uc-pos-017 directional family, from the control plane) · `dp_uc48_kernel` (xwobacon) · `barrel_rate.py`.
**Inherited by receipt:** the client's three cards (reproduced / graded, HP-01…HP-12); `uc-pos-001` layout.
**Generalised:** NF-2 (from `dp_uc49` NF-1), BF-1 (from `dp_uc49` CF-2).
**Introduced (provisional):** XW-1 PA xwOBA · HL-1 inner/middle/away · LR-1 LHP rank · TT-1 time through the order · IC-1 card composition.

## Defects found by building

- **D-50-1** `get_stats` cannot take `batter` as a level (`measure_calcs` renames it to `pitches`).
- **O-26** (second exposure) a `nphl` name filter drops 10 of Sale's 2026 pitches.
- **MV-1** Savant `woba_value` credits reached-on-error; house wOBA does not (gap up to .029, Sosa 2026 vs LHP).
- **D-1** (procedural) the bid was filed after the pre-game build; priced mechanically, reconciled in `07`.
