# 03 · Governance
**business-glossary-agent · metadata-mapper · data-dictionary · data-tagger · domain-steward-proxy**
`uc-pos-023-schwarber-2026-hr-animation-001` · UC #58 · `dp_uc58` v1.0.0

## 0 · Inheritance policy (Rule-1 searches run at T0)
| Searched for | Found | Decision |
|---|---|---|
| cumulative-by-PA engine | `cumulative_metric.py` (Harper BB%, Marsh XBH, Alvarado) | **inherit by import, sha-pinned** |
| WPA sign | `dp_uc51` pitching WPA (+dHWE home / −dHWE away) | mirror as WP-1 |
| hc → feet, direction | K40 `derive_loc` (PA-L1), `hit_direction` (cell 24) | inherit |
| park outline | K54 `CBP_DIMS` (cbp-spray SoT) | inherit |
| pitch group | K57 `client_pitch_group` (CPG-1) | inherit (the client's own map) |
| ball diameter | none in repo | define PM-1 (2.9 in) |
| HR barrel share | none (only per-BIP `barrel_rate_g`) | define HB-1, distinct name (alias rule) |
| prior Schwarber UCs | UC21, UC33 | entity lock, NULL standard |

Pins: `dp_uc57_kernel.py` `601e958a…`, `cumulative_metric.py` `a2888740…`, plus 17 through K57. **18 unique files, all PASS** (V01).

## 1 · Glossary additions (provisional, DPO to ratify)
- **HB-1 HR barrel share**: barrels / HR. Its display label is "HR that were barrels", never "barrel rate".
- **WP-1 batter WPA**.
- **CP-1 cumulative HR by PA**.
- **HL-1 highlight rules**.
- **SP-1 / SP-2 / SP-3 spray placement**.
- **PM-1 pitch-map drawing rule**.
- **GR-1 grade bars**.
- **DH-1 game order**: a defect fix, proposed for the house (§3).

## 2 · Data dictionary: published receipts (`out/dp_uc58_*`)
| File | Grain | Key columns |
|---|---|---|
| `cum_hr_by_pa.csv` | PA × season | game_year, cum_pa, cum_num (HR), era |
| `season_table.csv` | season | game_year, team, pa, hr, pa_per_hr, hr_rank (min-rank ties) |
| `hr_quality_by_season.csv` | season | total_hrs, max_ev, mu_ev, max_dist, mu_dist, barrels, hr_barrel_share (HB-1), bips, bip_barrels, barrel_rate, bip_mu_ev |
| `hand_group_by_season.csv` / `rhp_fastball_by_type.csv` | season × hand × group / type | HB-1 panel + call ("too few to call (EV)" under 5 HR) |
| `hr_register_2026.csv` / `hr_non_regular_2026.csv` | HR | PITCH_KEY, season_hr_no, cum_pa, wpa (WP-1), walkoff, result, go_ahead, tags (HL-1), pitcher_name + source |
| `spray_2026.csv`, `cbp_outline.csv` | HR / bearing | bearing_deg, x_ft, y_ft, approx (SP-2), field (DR-1) |
| `pitchmap_2026.csv` | HR | plate_x, plate_z, pitch_group (CPG-1), in_drawn_zone |
| `clip_list.csv` | clip | game_pk, inning, inning_topbot, at_bat_number, pitch_number (the `resolve_play_ids.py` keys) + scene, beat, label |
| `design_data.json`, `brand_tokens.json`, `keyframes_manifest.json`, `headlines.json` | — | the prompt's DATA block; tokens; keyframe names; every headline at 6 dp |
| `hp_grades.csv`, `dq_scorecard.csv`, `cp1_client_vs_governed_axis.csv`, `verification.csv` | — | grades, DQ, CP-1 evidence, harness |

**Tagging (data-tagger):** public-figure performance data; domain = Phillies Offense (`pos`); sensitivity = internal (publish decision is the DPO's). No PII.

## 3 · Findings for the house (domain-steward-proxy)
1. **DH-1 (new, house-wide):** `cumulative_metric.cumulative_frame` sorts by (game_date, game_pk, at_bat_number), but game_pk order is not game order on doubleheader days. On 2026-04-30, 823472 was Game 1 (MLB.com: 350th career HR off Logan Webb). Every house cumulative chart puts a DH day's PAs in the wrong order when game_pk runs backwards. Totals are unaffected; steps move by up to one game's PAs. `sv_id`, the natural fix, is null in 2017–26. **Proposed:** `cumulative_metric` v1.1 accepts an `order=` column. This UC wraps it without editing the pinned file.
2. **PA-X1 (recurrence of UC57 SRC-PA):** `cumulative_metric`'s default `pa_exclude` drops only `truncated_pa`. Callers that don't pass the house `NON_PA` list count baserunning-out rows as PA (Schwarber 2021: 473 vs 470). Recommend making `NON_PA` the default in v1.1.
3. **NA-1 (recurrence):** `(s == 6).mean()` on a nullable column drops NA rows from the denominator. The house `barrel_rate_g` is right (barrels / all BIP). The harness first got it wrong and fixed its own check (`05` §2).
4. **WP-1:** raw `delta_home_win_exp` is home-team perspective. Any "biggest swing" ranking on it buries road heroics (6/28 at NYM ranks 45th of 45).
