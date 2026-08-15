# 02 · Engineering Design
**data-architect · kpi-calculator · join-validator · eda-agent**

## Grain layers

| Layer | Grain | Rows | Purpose |
|---|---|---|---|
| L0 context | `player_name` × `game_year` | 217 hitter-seasons (98 players, ≥50 PA) | AP-9 benchmark pool |
| L1 monthly | `player_name` × `game_year` × `month` | 6 | primary curated frame `z` |
| L2 rolling | `game_year` × `cumulative_pa` | 2,822 | AP-6 hero |
| L3 game | `game_pk` | 11 | streak drill — **counts only, no rates** |

## KPI register

| ID | KPI | Status | Source |
|---|---|---|---|
| — | PA / slash / wOBA | INHERITED (rebuilt unrounded) | `nresults`, seasonal constants |
| AP-1 | `fpsr` | **INHERITED-APPROVED** | notebook; `cde.fpsr` approved |
| AP-2 | `swing_rate` | NEW-PROVISIONAL | swings ÷ pitches, governed SWINGS |
| AP-3 | `srfp` | NEW-PROVISIONAL | AP-2 on `pitch_number==1` |
| AP-6 | rolling wOBA by cum PA | **INHERITED-VARIANT** of RF-1 `running_line` | re-indexed game_date → cum PA |
| AP-9 | `discipline_ratio` | NEW-PROVISIONAL | BB/K from counts |
| AP-10 | `walks_between_ks` | NEW-PROVISIONAL | run length; ordered |
| — | chase / whiff / OOZ-whiff / hard-hit / barrel / EV90 | INHERITED | notebook |

**OOZ whiff rate** uses the `uc-cat-001` same-filter-both-sides correction:
`count(ooz & swing & whiff) / count(ooz & swing)`. It is the H1-vs-H2 discriminator.

## Join validation

| Check | Result |
|---|---|
| L1 merges — row count stable at 6 across 10 merges | ✅ no fan-out |
| `first_pitches` sum == PA sum | ✅ 458 == 458 |
| monthly PA sum == season PA | ✅ 458 |
| `swings` in AP-2 == `swings` in whiff_rate denominator | ✅ same population by construction |
| left-merge NULLs | rates NULL where denominator absent; **no blanket fillna** |

## EDA notes
- wOBA path .238 → .316 → .351 → .347 → .451 — **two step changes, not a smooth ramp.**
- Chase and OOZ-whiff both fall in August; chase falls on the larger base.
- FPSR falls monotonically Apr → Aug (.671 → .411). **This is the confound and it is large.**
