# 03 · Governance
**business-glossary-agent · metadata-mapper · data-dictionary · data-tagger · domain-steward-proxy**
`uc-pos-024-schwarber-2026-recap-001` · UC #60 · `dp_uc60` v1.0.0

## 0 · Inheritance (Rule-1 searches at T0)
| Searched for | Found | Decision |
|---|---|---|
| prior Schwarber UCs | UC21, UC33, UC58 | inherit K58 (career loader, DH-1, WP-1, HB-1); UC33 SW-8 + OI-1; cite UC58 HR grades |
| recap spine | K57 (`dp_uc57_kernel`) via K58 | inherit by import |
| hitter pools | K54/K57 `hitter_seasons` (KP-1 ≥ 50 PA; PR-1 context ≥ 200 PA) | register both as SD-1 |
| pitcher pools (for Tier 3 later) | CX-1 ≥ 150 pitches (K49), CX-1b ≥ 2000 pitches (uc-pps-034), RP-1 reliever role (K52) | registered as SD-1 entries, SP and LHP-relief marked DRAFT |
| ASB constants | `"2026-07-13"` (K49), `"2026-07-14"`, `"2026-07-16"` (several kernels) | SD-2 `asb_2026` window; equivalence asserted |
| Wheeler slide | dp_uc51 SR-2 `STRETCH_FIRST/LAST` 7/27–8/24 | SD-2 `wheeler_2026_slide` by reference |
| breakpoint scan | K40 RC-5 (`breakpoint_scan`, wOBA metrics) | reused; generalized to xwOBA (`xwoba_scan`) |
| trendline / R² / IQR helpers | none in repo | built SD-3 `phillies_dp/recap_viz.py` |

**Pins:** K58 chain (18 files) + `recap_viz.py` `e6c9436a…` + `comparison_sets.json` `852b9765…` + `eras.json` `3ace7b10…` = **22, all PASS**.

## 1 · House assets created (version-controller: additive, non-breaking)
| Asset | Path | What it governs | Status |
|---|---|---|---|
| SD-1 | `data/_schema/comparison_sets.json` | 5 sets: hitter ≥ 200 / ≥ 50 PA (APPROVED); pitcher house log CX-1 (APPROVED); SP seasons, LHP relief (DRAFT, DPO to ratify for Tier 3) | v1 |
| SD-2 | `data/_schema/eras.json` | `asb_2026`, `wheeler_2026_slide`, `schwarber_2026_back`, `schwarber_2026_absences` | v1 |
| SD-3 | `phillies_dp/recap_viz.py` | V1–V7 text; `trendline_r2`, `above_below`, `dot_sizes`, `context_box`, `discrete_dots`, `sketch_trend`, `audit`; self-test (`python -m phillies_dp.recap_viz`) | v1; house selftest 11/11 unaffected |

## 2 · Glossary (provisional, DPO to ratify)
- **BK-1** back test: grade vocabulary CONSISTENT WITH A PHYSICAL CHANGE / PARTLY / NOT VISIBLE IN THE LOG. It never uses "caused".
- **POP-1** lost-pop test: 4 legs (EV p90, barrel %, ISO, HR/PA) vs his 2022–25 range.
- **CN-1** concern test: an xwOBA leg plus a process leg (K% and chase both CHANGED).
- **Tier 3 visual standard V1–V7:** this UC is the first adopter; text lives in `recap_viz.STANDARDS`.

## 3 · Data dictionary: published receipts (`out/dp_uc60_*`, 37 files)
`season_panel`, `context_pool_200`, `by_month_2026`, `by_half_2026`, `bk1_pre_post`, `bk1_xwoba_scan`, `bk1_woba_scan`, `ev_bip_2022_26`, `hand_group_2025_26`, `by_hand_2022_26`, `cum_woba_by_pa`, `bat_speed_swings_2026`, `dumbbell_hand_group`, `hard_hit_labels.json`, `hp_grades`, `dq_scorecard`, `visual_audit`, `figure_specs.json`, `headlines.json` (every headline at 6 dp), `f1`–`f8` JSON + PNG, `season_card.png`, `verification`.

**Tagging (data-tagger):** public-figure performance data, domain `pos`, internal until the DPO publishes. No PII.

## 4 · Findings for the house (domain-steward-proxy)
1. **ER-0:** three ASB constants. SD-2 now owns the definition; kernels should read `recap_viz.era("asb_2026")`.
2. **CAT-1:** plotly treats numeric-looking category strings as linear when an annotation uses one as x. Every season-category chart in the repo is exposed. Force `type="category"`.
3. **Two bat-speed populations:** K40 `bat_tracking` counts all tracked swings; BP-0 drops bunts and degenerate swings below 25 mph. They differ by ≈ 0.25 mph here. Each figure must say which one it shows (F4 now prints both).
4. **The K–chase relation is near zero** across Phillies hitter seasons (R² < 0.01, n = 117). Chase and strikeouts should be coached as separate problems.
