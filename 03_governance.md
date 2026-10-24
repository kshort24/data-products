# 03 · Governance
**business-glossary-agent · metadata-mapper · data-dictionary · data-tagger · dq-rule-definer**
`uc-pos-022-turner-2026-recap-001` · UC #57 · `dp_uc57` v1.0.0

## 0 · Rule-1 inheritance (imported by pinned hash, never copied)
| File | sha256 (16) | What it brings |
|---|---|---|
| `dp_uc56_kernel.py` (control plane, UC56) | `2965b435ecdad004` | WB-2 pooled-season wOBA wrapper, `client_frame(name)`, `pull_air` (K46) |
| → `dp_uc55_kernel.py` (MLB root, K55) | `9bdcce59794e21aa` | K54 spine (slash/wOBA/xwOBA, chase/whiff/swing/HH/barrel fixes, CR-1, XW-1, KP-1, `two_prop_z`, CM-1), `directed_bip` |
| → `dp_uc40a_kernel.py` (UC40 folder, K40a) | `807986c0396fcf56` | BP-0/BP-1/BP-2, PU-1/PU-2, PB-1, conventions C1-C8 (O-15) |
| → `barrel_rate.py`, `dp_uc46_kernel.py` and 12 more through K54 | — | client barrel function, directional family |

`assert_lineage()` re-asserts **17 unique files** at every build and in the harness (V0). The BID said "14 pins"; the count is higher because UC57 pins K56, which adds K56, K46 and `barrel_rate.py` above K55's 14 (duplicates collapse by file name).

## 1 · Glossary decisions
| Term | Decision |
|---|---|
| **PR-1 pitch-recognition gap** | NEW, provisional. Swing gap = IZ swing − chase; contact gap = IZ contact − OOZ contact. Zone 1-9 vs 11-14; rows with `pitch_type` only (AB-1) |
| **VS-1 velo segment** | ADOPTED (client). Governed frame excludes null velo (0 affected LHP fastballs in 2026; 0 in 2023-26) |
| **CT-1 change call** | NEW. Bars and floors exactly as the BID's pre-registration |
| **PP-1** | NEW. Rule as the BID's pre-registration; stored as `K.PP_RULE` and printed into H |
| **XW-1c xwOBA on contact** | Section B generalization of XW-1 (same atom on BIP PA ends); not a new KPI |
| **CPG-1** client pitch groups | The notebook's `group_map` maps KN → Breaking; the house map has KN → offspeed. Client tables use the client map (reproduction); governed tables use the house map |
| "Atrocious" | client term; reported, never a threshold |

## 2 · Amendments
None to the pre-registration. One mechanics note, disclosed rather than amended: the BID named `two_prop_z` as "the change test". It tests one proportion; the PR-1 **gap** is a difference of two proportions, so its z uses the unpooled Wald SE of the four legs. The CT-1 bars (1.96 / 1.00) and floors are unchanged, and each leg is still tested with `two_prop_z`.

## 3 · Metadata map (physical → business)
`attack_angle` → attack angle · `swing_path_tilt` → swing-path tilt · `intercept_ball_minus_batter_pos_x_inches` → `intercept_side_in` (lateral) · `..._y_inches` → `intercept_depth_in` (depth) · `attack_direction` → pull-negative (O-15; `pull_direction` = −value). Mapping done once, in K40a `with_bat_path`.

## 4 · Tags
Domain `pos` · subject area hitting process · sensitivity INTERNAL (performance data on a named MLB player; no PII beyond the public name and MLBAM id). Contract terms (CI-2) are public reporting.

## 5 · DQ rules (scored in 05)
LIN-1 pins · ANC-1 anchor · BP-C conventions · ENT-1 id lock · DUP-1 key · SRC-4 game types (WARN by design) · SRC-5 career context · CI-1 reconcile · CM-1 endpoints · PR-1 floors · REC-40a partial-season reconcile · BP-W window (WARN) · SM-1 small cells (WARN).
