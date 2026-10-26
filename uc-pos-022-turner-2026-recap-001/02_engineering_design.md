# 02 · Engineering Design
**data-architect · kpi-calculator · eda-agent · join-validator**
`uc-pos-022-turner-2026-recap-001` · UC #57 · `dp_uc57` v1.0.0 · written at T1 (2026-10-23)

## 1 · Model
| Layer | Grain | Source | Key | Notes |
|---|---|---|---|---|
| Pitch (subject) | pitch | `data/phillies/phils_2023..2026.parquet` via LP-1 (`K49.load_phils_cols` + `K54._prep`) | `game_pk × at_bat_number × pitch_number` | `batter == 607208`, `phillies_role == 'batting'`, `game_type == 'R'`; 0 duplicate keys (EN-2 assert) |
| Career context | pitch | `data/opponents/turner.parquet` | same | 2016-22, locked by id; never pooled into the baseline |
| Client frame | pitch | `K56.client_frame('Turner, Trea')` | same | nphl + pos, no `game_type` filter (SRC-4/5); used only by `dp_uc57_hp.py` |
| Cell | `period × p_throws × pitch_group` | subject pitch layer | — | `period` = `2023-25` / `2026`; groups = K54 `PITCH_GROUP` |
| Peer cohort | batter × season | all Phillies batting rows 2025-26 | `batter` | PB-1 gate: ≥ 200 tracked swings in both seasons (8 hitters) |
| PR-1 context pool | batter × season × hand (× group) | Phillies 2023-26 | — | hitter-seasons ≥ 200 PA (41 RHP cells); group cells need ≥ 50 swings |

No joins beyond the cohort membership filter (`isin`), so there is no fan-out surface. The only merges are same-grain merges of inherited function outputs inside `cell_panel` (left merges on the level; count columns filled with 0, never with a rate).

## 2 · KPI specs
| KPI | Status | Definition | Denominator | Floor |
|---|---|---|---|---|
| Swing, whiff, chase, IZ swing/whiff, OOZ whiff, HH, barrel, popup | inherited (K54 / K40a PU-2) | as certified | pitches / swings / OOZ pitches / BIP | CT-1 floors |
| Contact, IZ contact, OOZ contact | inherited (1 − whiff on the same filter) | — | swings on that filter | 50 |
| xwOBAcon (**XW-1c**) | Section B (XW-1 on BIP PA ends) | Σ estimated_woba (fallback woba_value) / Σ woba_denom over BIP | BIP | reported with n; no test |
| **PR-1** swing gap / contact gap | NEW, provisional | IZ swing − chase; IZ contact − OOZ contact | four legs | 50 per leg |
| **CT-1** change call | NEW (pre-registered) | pooled two-proportion z (inherited `two_prop_z`), 2026 vs 2023-25 counts | rate's own | 30 BIP / 50 |
| PR-1 gap z | NEW (pre-registered as "change test"; mechanics here) | Δgap / √Σ p(1−p)/n over the four legs (unpooled Wald, independent samples) | — | 50 |
| **VS-1** velo segment | adopted | `release_speed > 94.9` High Velo, else < 95; governed frame drops null | — | — |
| **PP-1** path → popup rule | NEW (pre-registered) | SUPPORTED iff 2026 breaking-ball popup tilt ≤ non-popup tilt − 2.0° AND breaking popup rate CHANGED upward | tracked BIP | 10 BIP per side (PU-1) |
| PB-2 peer delta by group | Section B | PB-1 on PB-1's own cohort, at `pitch_group` grain | tracked swings | none (cohort fixed) |
| wOBA contribution by group | Section B | Σ_g (share26·wOBA26 − shareB·wOBAB); exact identity for the hand total | wOBA denominator | — |

## 3 · EDA
- `eda/dp_uc57/turner_reg_2023_26.md` (T0) and `eda/dp_uc57/turner_reg_2023_26_build.md` (T1; 9,778 × 92). Written by `phillies_dp.eda.to_file`; nothing printed to context.
- Nulls that matter: `launch_speed_angle` / `estimated_*` 80.8% null (non-BIP rows; expected). Bat-path fields null before 2025 (G7).

## 4 · Join-validator
No join changes cardinality: every merge is same-level on outputs of inherited group-bys. Row count of the subject frame is asserted twice (EN-2 in `subject_rows`, V1 in the harness).
