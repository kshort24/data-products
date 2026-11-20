# 03 · Governance
Agents: `kpi-calculator` · `technical-lineage-builder` · `dq-rule-definer` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search before declaring anything new
| Candidate | Search | Hit | Decision |
|---|---|---|---|
| RHP relief comparison set | `data/_schema/comparison_sets.json` | `phi_lhp_relief_seasons` (DRAFT, LHP-bound) | **CS-A** mirror for RHP (DRAFT), non-breaking |
| pitch × hand context | K44 `benchmark_population` (single pitch type, all roles), UC #63 pitch-type pool | partial | **CS-C** (relievers, by batter hand, ≥ 50) |
| late-close usage | K63 FN-1 (`entry_inning >= 7 & lead -1..3`) | found | **LC-1 = FN-1 reused unchanged** |
| cumulative wOBA | `cumulative_metric.py` (house skill) | found | **CW-1** = `cumulative_frame` with a house-weight metric dict, endpoints reconciled |
| cumulative usage | none (client did by month) | 0 | **CU-1 new** |
| inner-third share | none | 0 | **IN-1 new** |
| stint split | K63 ST-1 (MLB/AAA tiers) | partial | **S-1** gap rule (> 12 days) within MLB |

## 1 · Inheritance (`technical-lineage-builder`)
`dp_uc66_kernel.py` (sha `e672dbfadbe0…`) imports, never copies. `assert_lineage()` asserts `dp_uc64_kernel.py 32a83b8491dd…` and through it the full chain
(`dp_uc63_kernel` → K62 → K53 → K52 → K51 → K50 / K49 / K48 / K44 + `barrel_rate.py` + `cumulative_metric.py` + `phillies_dp/recap_viz.py`) at every run.
The client's notebook functions (`nresults`, `whiff_rate`, `chase_rate`, `fpsr`, `putaway_rate`, `hard_hit_rate`, `barrel_rate`, `lhb/rhb_pitch_mix`) are the K44 Section A transcriptions.

## 2 · New KPI specs (`kpi-calculator`; filed in the BID 14:12 ET, before code)
### CU-1 cumulative pitch usage (provisional)
- **Plain language:** after each appearance, the share of all season-to-date pitches (to that batter hand) that were each pitch type.
- **Formula:** cumsum(count of type through appearance a) / cumsum(pitches with a pitch type through a). **Grain:** batter-hand × appearance × pitch type.
- **Edge cases:** automatic balls (null `pitch_type`) excluded from numerator and denominator (K44 `pitch_mix` keeps them in its denominator — differs by ≤ 0.2 pt; DQ-17). Endpoint asserted = season value_counts (DQ-12).
### CW-1 cumulative wOBA / xwOBA against (provisional)
- House `cumulative_metric.cumulative_frame` with metric dicts: wOBA = FanGraphs weights (wBB, wHBP, w1B, w2B, w3B, wHR) / PA (events not null, not `pickoff_1b`); xwOBA = XW-1 rows. Noise floor 25. Endpoints asserted equal to K44 `mcgs` wOBA and K50 XW-1 (tol 1e-9) for All and each hand.
### IN-1 inner-third share
- Share of a pitch type to a hand with `plate_x ≥ +0.277 ft` (LHB) or `≤ −0.277 ft` (RHB), catcher's view. Null locations excluded.
### CS-A / CS-B / CS-C — see `02` §1. Percentiles via KP-1 `house_percentile` (subject excluded; ties share the better rank).
### S-1 command by stint
- Stint = run of MLB outings with no gap > 12 days. KPIs per stint from the same kpi block as the season.

## 3 · Visual rules VZ-1…VZ-6 (provisional; proposed recap-wide)
| Rule | Statement | Check |
|---|---|---|
| VZ-1 | the title states the finding; subtitle names the comparison set, n and the caveat | eyeball |
| VZ-2 | one scale per metric (small multiples); no mixed-scale rates on one axis | per-panel axes (F1, F2, F7, F8, S1) |
| VZ-3 | right = better on every rate panel (flipped where lower is better), and labelled | axis titles |
| VZ-4 | no free-floating in-plot labels that can collide: values live in ticks, legends, panel titles or the right margin | eyeball (2 rounds) |
| VZ-5 | pitch palette = house hues, lightness-adjusted to ≥ 2.4:1 contrast on white (min achieved 3.03) | machine (`palette_min_contrast`) |
| VZ-6 | pitch maps show where pitches live (every pitch / density), never a mean-location bubble | F4a, F4b |

## 4 · Privacy (`privacy-watchdog`)
Public-figure, on-field performance data from public Statcast; no PII; batter names not used. Clear for external publish.

## 5 · Tags (`data-tagger`)
Sensitivity: public · Domain: Phillies Pitching · Subject area: pitcher season recap · Product: `uc-pps-042`.

## 6 · Change classification (`version-controller`)
v1.0.0 initial. Corrections made before publish and after first compute: (a) report/F7 text on June zone rate (house-rule tie with September, DQ-17) — **non-breaking** (text, no bar or number changed); (b) DQ-17 added — non-breaking. No HP bar changed after compute.
Breaking for any successor: changing CS-A's role rule or floor, CU-1's denominator, or any HP bar.
