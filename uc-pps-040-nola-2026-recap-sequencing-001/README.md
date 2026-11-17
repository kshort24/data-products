# Better Process Than Results, and a Book Built on the Curve — Aaron Nola 2026 Recap + Pitch Sequencing

**UC #64 · `uc-pps-040` · `dp_uc64` · v1.0.0 · delivered 2026-11-16 · READY-CONDITIONAL (C1–C4) · harness 43/43 · DQ 21/3/0 · V1–V7 10/10**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here
| If you want | Open |
|---|---|
| the story on paper | `dp_uc64_nola_2026_recap_report.pdf` (12 pages) |
| the story, clickable, with the Sequence Explorer | `dp_uc64_nola_2026_dashboard.html` or the Artifact "Aaron Nola 2026" |
| the bid and the award | `BID_2026-11-16_uc-pps-040-nola-2026-recap-sequencing.md` |
| the client's three rulings | `intake/client_prompt_2026-11-16.md` |
| what the org decided and why | `00_dpo_orchestration_record.md` |

## The answer in eight lines
1. 2026: .343 wOBA (5th pct of 40 Phillies SP seasons) but .315 xwOBA (27th); HR/PA 5.0%, last in the pool; whiff 65th, chase 77th, CSW 67th.
2. The curve earned +1.1 runs/100; four-seam −2.1, sinker −2.8, cutter −3.0. The damage was the fastballs.
3. 1H .355 → 2H .327 wOBA, xwOBA nearly flat; August best. The 7/05 pivot held (CH 12.6% → 20.1%); CH vs LHB wOBA regressed .192 → .311.
4. Best ending: two straight curves (.222 xwOBA vs LHB, .174 vs RHB); FF→KC→KC best three-pitch finish on both sides.
5. Setups that add value: SI→CH (+3.2) and SI→FF (+2.3) vs RHB; CH→KC (+1.8) vs LHB. Costliest: CH→FF vs RHB, SI→KC→KC vs LHB.
6. 28 of 176 rankable sequences clear their 90% interval vs 17.6 by chance (p = .009): real in aggregate, candidates individually.
7. Young era → 2025–26: 0 of 43 FADED, 3 GREW (all vs LHB). The double curve to RHB is the one staple that slipped (inside the noise).
8. Batterymates: same book to RHB; vs LHB Stubbs games differ (p = .002, holds on 2023–25), small. S-1: least predictable mix of his career.

## Package
```
BID_…md · 00–07 · README · uc-pps-040 contract (copy) · ledger patch (copy) · intake/client_prompt_2026-11-16.md
dp_uc64_nola_2026_recap_report.md/.pdf · dp_uc64_nola_2026_dashboard.html
data/     key receipts (headlines, seasons, context pct, starts, prior re-read, seq_career, seq_by_era, endings, era drift, book test, calibration, PI-1, DQ, verification, visual audit)
figures/  10 PNGs (F1–F9, S1)
```
Code and all 63 receipts live at the MLB root (`dp_uc64_*.py`, `out/dp_uc64_*`, `eda/dp_uc64/`). Re-run: `04` §1.

## Governed objects
Inherited (pinned import via K63): K44 KPI functions, K48 rv100/xwobacon/arsenal/KP-1, K49 GS-1/OU-1/CX-1, XW-1, BR-1, CSW, SD-1/SD-2 registries, recap_viz.
Client function: SQ-0 `pitch_sequence` (verbatim). New, provisional: PT-H, SQ-1…SQ-6, SQ-5d, OUT-1, **PC-1 (DPO-defined)**, PI-1.
