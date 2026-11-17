# 02 · Engineering Design
Agents: `data-architect` · `kpi-calculator` · `eda-agent` · `join-validator`

## 1 · Model (no new physical tables; pandas frames over the house log)
| Object | Grain | Key | Built by |
|---|---|---|---|
| `nr` subject frame | pitch | (game_pk, at_bat_number, pitch_number) | `K.subject_frame` (id lock, O-26 assert, dedup assert) |
| `d` sequencing frame | pitch | same | `K.harmonize` (PT-H) + `K.outcome_cols` (rv, csw, swing, whiff, bip, pc1, xw_num/den, out_pa, k_pa) |
| windows `W[k]` | window (end pitch) | PITCH_KEY of end pitch + k | `K.windows(d, k)` (SQ-1) |
| baselines `B` | pitch type × balls × strikes × side (× era / year) | LIFT_KEY | `K.baselines` |
| PA table | completed batter PA | (game_pk, at_bat_number) | `K.pa_table` |
| endings | PA × k | PA key + k | `K.endings` (SQ-3) |
| SP pool | pitcher × season (≥ 2,000 R pitches) | (pitcher, game_year) | SD-1 `phi_sp_seasons` |

## 2 · KPI calculation specs (`kpi-calculator`) — Section C of the kernel
| ID | Formula | Edge cases |
|---|---|---|
| SQ-2 | `100 × mean_j[(−dre_j) − b(pt_j, balls_j, strikes_j, stand)]` over windows ending at j | rv null (22 pitches) → excluded from the mean; baseline join validated 0 unmatched (`many_to_one`) |
| CSW lift | `mean(csw_j − b_csw)`; whiff lift on swings only `mean(whiff_j − b_whiff | swing)` | b_whiff null when the cell has no swings → lift NaN, excluded |
| SQ-3 | per PA: out (OU-1 > 0 on terminal), K, PC-1 (tracked BIP), XW-1 num/den, ending RV = −Σ dre over last k | PA length < k excluded; XX-containing endings dropped |
| SQ-4 | shrunk = lift × n/(n+100); endings xwOBA shrunk `(num + 50·side_xwoba)/(den + 50)`; bootstrap: resample whole PAs, 1,000 reps, seed 64 | windows inside one PA are dependent → cluster by PA |
| SQ-5 | era-internal baselines; FADED iff lift(E1) − lift(E3) ≥ 1.5 and 90% CI of diff excludes 0, both n ≥ 30 | 2024 in no comparison window; G6 sensitivity E1s 2017–19 / E3s 2024–26 |
| SQ-5d | raw = baseline part + lift (identity); base = raw − lift | descriptive, added 2026-11-16 after first compute; **non-breaking** (no bar changed) |
| SQ-6 | GJSD of pair-usage rows (catchers, weighted by total) vs 500 within-season permutations of game-level catcher label; p = (1 + #null ≥ obs)/(1 + reps) | catcher = `fielder_2` of Nola's first pitch of the game; ≥ 8 starts in scope |
| PI-1 | `H(next | side)`, `H(next | prev, side)`, IG = difference; plug-in entropy, bits | Nola PT-H applied; others raw tags; pool ≥ 2,000 pitches |
| OUT-1 / PC-1 | OU-1 outs > 0 on PA terminal / LSA ∈ {1,2,3} on tracked BIP | non-PA terminals (pickoff, CS, truncated_pa) excluded |

## 3 · Join validation (`join-validator`)
| Join | Expectation | Result |
|---|---|---|
| windows → baselines (career, era, year) | many-to-one, 0 unmatched | PASS (pandas `validate="many_to_one"`; DQ "SQ-2 k=* baseline join" PASS ×3) |
| PA table ↔ client `pitch_sequence()` seq | 1:1, identical token strings | PASS (1.0000 identical) |
| windows → game catcher | many-to-one by game_pk | PASS (0 null `fielder_2`) |
| catcher id → name (batting rows, modal) | 1 name per id; matches `uc-pps-027` authority | PASS ×3 (Realmuto, Stubbs, Marchán) |
| starts → GS-1 / XW-1 / nresults | 1 row per game_pk | PASS (33 = 33) |

## 4 · EDA (`eda-agent`)
`phillies_dp.eda.to_file` → `MLB/eda/dp_uc64/nola_regular_2015_2026.md` (no frames printed to context). Findings that shaped design: PA-length distribution
(1–4 pitches = 64% of PAs) → windows, not full strings; CU/KC relabel → PT-H; cutter only from 2021 → structurally THIN E1 cutter cells; 2025 short season → recent-era power limit.
