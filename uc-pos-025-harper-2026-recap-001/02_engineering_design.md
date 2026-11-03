# 02 · Engineering Design
**data-architect · kpi-calculator · eda-agent · join-validator · dq-rule-definer · dashboard-specifier**
`uc-pos-025-harper-2026-recap-001` · UC #61 · `dp_uc61` v1.0.0

## 1 · Model (data-architect)
| Frame | Grain | Source | Notes |
|---|---|---|---|
| Subject | pitch | `load_career()`: house log 2019–26 (Phillies batting) ∪ `opponents/harper.parquet` 2015–18 | MLBAM 547180; `PITCH_KEY` unique across sources; DH-1 `game_seq` + DH-2 override; house wOBA weights on both sources |
| PA ledger | PA | `pa_ledger()` over the subject frame | `nresults_unrounded` counting definitions; house-weight wOBA num/den per PA |
| Cumulative | PA × season | `cum_slash()` (CM-2) | running sums within `game_year`; rates blank before 25 PA |
| Envelope | PA | `career_envelope()` | Washington 2015–18 and Phillies 2019–25 min/median/max + `n_seasons` |
| Pitch map | pitch (2026) | `tag_regions()` (UC #23) + DMG-1 flags | 13 pitches without location dropped from the map (LOC-1) |
| Spray | BIP (2026) | `spray_frame()` = PA-L1 + DR-1 | LHB convention asserted (pulled grounders median `loc_x` > 0) |
| Pool | batter × season | K57 `hitter_seasons` on the house log, ≥ 200 PA (SD-1 `phi_hitter_seasons_200`) | 122 seasons |
| Positions | game (2026) | Phillies pitching rows, `fielder_2..9` | 1B / RF / DH-or-none ledger; defensive-only games found here |

Join validation: no row-level joins on the pitch frame. The two sources are concatenated, then asserted 0 duplicate keys (EN-2). Panels merge 1:1 on their level keys.

## 2 · Specs (kpi-calculator)
| ID | Spec | Status |
|---|---|---|
| `load_career` | K58 loader with the subject as parameters; WSH rows re-weighted with `K49.apply_woba_weights` | generalization (Section B) |
| CM-2 `cum_slash` | BA = H/AB · OBP = (H+BB+HBP)/(AB+BB+HBP+SF), BB incl. IBB · SLG = TB/AB · wOBA = Σnum/Σden (IBB out) · HR count | generalization; endpoints == `nresults_unrounded` to 1e-9 (CM-2 DQ) |
| `hand_group_panel` | `season_panel` at (p_throws, pitch_group, game_year); share within hand; SM-1 floors 30 PA / 15 BIP | generalization |
| DMG-1 | `type == X & launch_speed ≥ 95` or HR | new, provisional |
| AP-1 / HC-1 / OZ-H | BID §3 (18:05 ET) | grade rules, provisional |
| `ch1` | K60 two-proportion call, |z| ≥ 1.96 CHANGED, 1.00–1.96 LEANS | consumed |

## 3 · EDA (eda-agent)
`eda/dp_uc61/harper_reg_2015_26.md` and `harper_reg_2026.md` (never printed). First look:
- the season line ties to CI-1 at T0;
- bat-tracking columns are ≥ 90% null across the career frame (2024+ only); they are not used on the card;
- `launch_speed` is nullable Float64, so `>= 95` returns NA on untracked BIP. This broke `~` at T2 (B-1).

## 4 · Visual spec (dashboard-specifier)
| Fig | Region | Form | V1–V7 notes |
|---|---|---|---|
| F1 | TL-b | cumulative wOBA by PA, 12 seasons; 2026 red 3.6 px; Phillies solid slate; Washington dashed light; 2019–25 band; navy dotted pooled 2019–25 | V1 exception (cumulative); V2 context = band + priors |
| F2 | TR | catcher's-view pitch maps, RHP | LHP; faint location marks for every pitch by group; solid damage marks; HR stars; zone + shadow band; three callouts per panel | V1 markers only; V2 context = faint marks |
| F3 | B | spray of 155 hits on one outline; outs as faint context; KPI strip with 2019–25 range | V1 markers only; reference lines tagged `meta=reference` |
| Card | all | PIL composition of F1–F3 + copy | reference layout only; the kit is the deliverable |

**Palette:** UC60's validated set (dataviz validator, white surface): 2026 red `#E81828`; slate `#8C96A6` / light `#C3C9D2`; groups `#E81828` / `#7A5CC7` / `#0E9384`; hit types single `#2E6FB5`, double `#0E9384`, triple `#7A5CC7`, HR `#E81828`. Each palette appears in one region only.

**Departure from UC58 (recorded):** UC58 drew every ball to scale on HR-only pitch maps. F2 carries 2,734 pitches, so it uses location marks; the legend and the brief say so.
