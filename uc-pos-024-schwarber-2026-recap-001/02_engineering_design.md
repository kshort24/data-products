# 02 · Engineering Design
**data-architect · kpi-calculator · eda-agent · join-validator · dq-rule-definer · dashboard-specifier**
`uc-pos-024-schwarber-2026-recap-001` · UC #60 · `dp_uc60` v1.0.0

## 1 · Model (data-architect)
| Frame | Grain | Source | Notes |
|---|---|---|---|
| Subject | pitch | K58 `load_career()`: house log 2022–26 (Phillies batting) ∪ `opponents/schwarber.parquet` 2015–21 | MLBAM 656941; `PITCH_KEY` unique; DH-1 `game_seq` order; wOBA weights by K49 |
| Pool | batter × season | house log 2015–26, Phillies batting, regular season | `season_panel(["batter","game_year"])`; CS-1 context ≥ 200 PA (122), ranks ≥ 50 PA (220), CN-1 ≥ 600 PA (33) |
| Eras | date windows | SD-2 `eras.json` | H1 ≤ 7/12, H2 ≥ 7/16; BK-1 pre 3/26–6/22, post 6/25–9/27 |
| Swings | swing | K57 `bat_path_population` (BP-0) | F4 only; BK-1 receipt uses K40 `bat_tracking` (tracked swings). Both reported, both verified (V08) |

Join validation: no row-level joins on the pitch frame. Pool and subject panels merge 1:1 on their level keys. The team schedule is checked against the subject's games for the absence ledger (AB-1).

## 2 · Specs (kpi-calculator)
| ID | Spec | Status |
|---|---|---|
| `season_panel` | K57 panel (nresults_unrounded + xwoba_pa + cell_panel) + EV p90 + SW-8 + bat_tracking + HR/PA, barrel and hard-hit on BIP | generalization (Section B) |
| `xwoba_scan` | RC-5 breakpoint scan over xwOBA, filter-over-atom; candidate cuts = team game dates 5/1–8/31; eligible ≥ 150 PA both sides | generalization |
| BK-1 / POP-1 / CN-1 | as pre-registered (BID §3); bars in `dp_uc60_kernel.py` Section C | grade rules, provisional |
| SW-8 | 20° < LA ≤ 32° on tracked BIP (UC33 bins) | consumed |
| `ch1` | pooled two-proportion z (K54 `two_prop_z`), |z| ≥ 1.96 CHANGED, 1.00–1.96 LEANS | consumed bars (CT-1 pattern) |

## 3 · EDA (eda-agent)
`eda/dp_uc60/schwarber_reg_2015_26.md` (25,803 × 98, never printed).
- First look found the turn in July (xwOBA .303), not at the 6/23 scratch.
- Bat speed was flat by month.
- The 2016 season is 5 PA; it is plotted and labelled.

## 4 · Visual spec and Tier 3 compliance (dashboard-specifier)
| Fig | Question | Form | V1–V7 notes |
|---|---|---|---|
| F1 | What happened | season dots (sized by PA) on per-year CS-1 boxes; xwOBA open diamonds (same units) | V1 dots, V2 boxes, V3 IQR, V7 same units |
| F2 | Pace | cumulative wOBA by PA, one line per season (`cumulative_metric`) | the V1 exception; prior seasons = context |
| F3 | When | monthly dots sized by PA; half-season aggregates as bars over eras; tenure range band | item-3 pattern (era aggregates as shapes) |
| F4 | Back | bat-speed IQR boxes by month vs 2024/2025 season boxes | V3 on a non-velocity metric |
| F5 | Pop | EV boxes by season + 2026 halves, 95 mph line, hard-hit % labels | item-4 pattern (Harper prototype superseded) |
| F6 | Pop | SW-8 share dots on CS-1 boxes | V2 + V3 |
| F7 | Concern | K% vs chase scatter, CS-1, dotted fit with **R² and n**, above/below stated | V4 |
| F8 | Concern | dumbbell rows (2025 → 2026) by hand × pitch group, PA printed | V5 replacement for bars (item-12 pattern) |

**Palette** (dataviz validator, white surface):
- era: red 2026 / blue `#2E6FB5` / slate. Navy failed the lightness band for marks, so it is kept for ink and headers only.
- hand: `#2E6FB5` / `#B9770E`: PASS.
- pitch group: `#E81828` / `#7A5CC7` / `#0E9384`: PASS on all pairs.

**Render QA caught two defects:**
- **CAT-1.** Numeric-looking category labels ("2015") plus an `add_annotation(x="2026")` made plotly treat the axis as linear. Every box collapsed onto 2015. Fixed by forcing `type="category"` and drawing labels as text traces. Recorded for `recap_viz` v1.1: `context_box` callers should pass string categories and avoid annotations at category x.
- **Clipped subtitles.** Long subtitles ran off the figure. Fixed with a 132-character wrap in `base()`.
