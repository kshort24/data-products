# 03 · Governance — `uc-pps-031`

Agents: `business-glossary-agent` · `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 1 · Rule-1 search and semantic consistency

| Candidate | Search result | Disposition |
|---|---|---|
| Edge Rate | `edge_rate(level, df)`: UC8, glossary-approved, Register v2 P16 = **A**, `BALL_FT` ratified | **Inherited verbatim** (Section A2, byte-identical to dp_uc38). Not in the notebook (E-2) |
| "Ahead in the count" | PD-7 (`uc-pps-017`) inline; Register P8 = "promote to `count_leverage(level, df)`" | **CL-1 = PD-7 promoted.** Formula unchanged; even/behind/three-ball shares added as a flagged extension |
| Peer-netted YoY | PB-1 `peer_delta` (`uc-pos-014`, batter side) | **PN-1** = pitcher-side adaptation; same return keys |
| "Shadow" | OZ `shadow_in/out` (rectangular ±ball, batter), Attack Zone `shadow` (0–0.33 ft outside, UC#11/`uc-pps-022`), `edge_rate` docstring "shadow band" | New compound terms **Shadow Zone / Shadow Miss**, built on Edge Rate geometry. Crosswalk published |
| `shadow_zone_rate`, `shadow_miss_rate`, `beyond_shadow_chase_rate`, `shadow_region`, `common_rail_rescore` | 0 hits | Free |
| SG-1 20-80 grade (second use) | `uc-pps-030` | **Considered and rejected**: single-rail population is 13 arms at 500 pitches |

**The three geometries, side by side.** `d` = Euclidean distance from pitch centre to the zone perimeter.

| Term | Inside the zone | Outside, d ≤ 1 ball | Outside, d > 1 ball | Corners | Constant |
|---|---|---|---|---|---|
| **Edge Rate** (governed) | edge if d ≤ ball | edge | — | rounded | `BALL_FT` |
| **Shadow Zone / Miss** (SZ, new) | in the shadow | in the shadow | **Shadow Miss** | rounded (same function) | `BALL_FT` |
| OZ `shadow_in/out` / `waste` | `shadow_in` if within ball | `shadow_out` | `waste` | **square** | `BALL_FT` after ruling |
| Attack Zone `shadow` / `chase` | heart / zone-edge (55%×60% inner box) | `shadow` if ≤ **0.33 ft** | `chase` | square | **0.33 (conflicts)** |

Measured disagreement on Sánchez's 10,985 tracked pitches: SZ vs OZ = 38 (0.35%, corners only); SZ vs Attack
Zone = 604 (5.5%). **Glossary note:** "Shadow Miss" ≡ OZ "waste" up to corners. It is not the Attack Zone "chase" region.

## 2 · KPI specifications (kpi-calculator) — all PROVISIONAL

### SZ-0 `shadow_region(df)`
- **Plain language:** Labels every tracked pitch as heart, edge in, edge out, or beyond (missed the shadow).
- **Formula:** signed distance `s` = governed `_dist_to_zone_edge` with sign −inside / +outside. heart: `s < −BALL_FT`; edge_in: `−BALL_FT ≤ s ≤ 0`; edge_out: `0 < s ≤ BALL_FT`; beyond: `s > BALL_FT`.
- **Grain:** pitch. **CDEs:** `plate_x`, `plate_z`, `sz_top`, `sz_bot` (per pitch). **Null:** any CDE null → `untracked`, excluded from every SZ denominator.
- **Edge cases:** exactly on the perimeter → edge_in; exactly one ball outside → edge_out (matches `edge_rate`'s `<=`).

### SZ-1 `shadow_zone_rate` / SZ-2 `shadow_miss_rate`
- **Plain language:** How often the pitch lands within one baseball of the zone, or doesn't.
- **Formula:** SZ-1 = (heart + edge_in + edge_out) / located. SZ-2 = beyond / located = 1 − SZ-1.
- **Companion:** `beyond_miss_depth_ft` = median `s` of beyond pitches (how far the misses land).
- **Invariant (asserted):** edge_in + edge_out ≡ governed `edge_rate` (max diff 0.0004 = rounding).
- **Floor:** publish a split with ≥ 50 located pitches; below that, show n.

### SZ-3 `beyond_shadow_chase_rate` — the client's proof
- **Plain language:** When the pitch misses the shadow, how often does the hitter swing anyway?
- **Formula:** swings (Baseball Functions SWINGS list) on beyond pitches / beyond pitches.
- **Null:** 0 beyond pitches → NaN (never 0). **Floor:** 50 beyond pitches for a split to be interpreted; n is printed on every split.
- **Distinct from** kernel `chase_rate` (`zone > 9`). SZ-3 excludes the near-miss band, where swings are often a hitter's reasonable judgement rather than a chase.

### SZ-4 `edge_out_chase_rate`
- Swings on edge_out / edge_out. The near-miss twin of SZ-3, reported for contrast.

### SZ-5 `shadow_miss_direction`
- **Plain language:** Where the misses go.
- **Formula:** for beyond pitches, compare horizontal exceedance `max(|x| − 0.83, 0)` with vertical exceedance. Vertical ≥ horizontal → high/low. Otherwise arm-side/glove-side, **mirrored by `p_throws`** (LHP arm side = +x; asserted via HBP sign and sinker `pfx_x > 0`).
- **Output:** counts and shares by direction.

### CL-1 `count_leverage(level, df)` — PD-7 promoted
- `pitch_share_ahead` = pitches with balls < strikes / pitches (pre-pitch count). `two_strike_pa_share` = distinct PA with a 2-strike pitch / PA. **Unchanged from PD-7.**
- Extension (flagged): `pitch_share_even`, `pitch_share_behind`, `three_ball_pa_share`.
- PA key `(game_pk, at_bat_number)`.

### PN-1 `peer_delta_pitcher`
- **Plain language:** How much did he move compared with arms measured on the same instrument in the same two seasons?
- **Cohort:** pitchers in the Phillies log (both roles) with ≥ 200 pitches in both years (12 arms for 2025/26; 6 at 500).
- **Output:** subject delta, peer median delta, netted delta, rank (1 = most negative). Returned on **native** and **2026-rail** bases.
- **Known limitation (O-18):** on native rails, a pitcher's exposure to the rail change depends on his vertical profile, so native netting is biased for low-zone arms. **Use the common-rail basis for any zone-geometry metric.**

### ZC-1 `common_rail_rescore`
- **Plain language:** Judge a 2025 pitch against the 2026 zone of the same hitter.
- **Formula:** replace `sz_top`/`sz_bot` with that batter's 2026 modal rails (inner join on `batter`); leave `plate_x`/`plate_z` untouched; re-run SZ. Coverage is reported.
- **Decomposition (receipt `rail_decomposition`):** native Δ = rail effect + common-rail Δ; common-rail Δ = league common-rail Δ + subject-specific. The identity is asserted.
- **Limitation:** it can't re-derive Statcast `zone`, so kernel `in_zone_rate` is decomposed through its geometric twin (4.0% disagreement).

## 3 · Technical lineage (technical-lineage-builder)

| Published number | Source columns | Transform chain | Receipt |
|---|---|---|---|
| Walk rate | `events` | kernel `get_stats` → `nresults.bbrate` | `season_panel`, `half_panel` |
| In-zone, chase | `zone`, `description` | kernel `chase_rate` | same |
| Pitches ahead | `balls`, `strikes` | CL-1 | same |
| FPSR | `pitch_number`, `type` | kernel `fpsr` | same |
| Edge Rate | `plate_x/z`, `sz_*` | A2 `edge_rate` | same + `geometry_crosswalk` |
| Shadow Zone/Miss, chase beyond | `plate_x/z`, `sz_*`, `description` | SZ-0 → SZ-1..4 | panels, `split_tests` |
| Miss direction | + `p_throws` | SZ-5 | `miss_direction` |
| League deltas | all pitchers | same functions, population swap | `league_control` |
| Rail audit | `batter`, `sz_*` | groupby batter-season | `zone_rail_audit` |
| Decomposition | + 2026 rails | ZC-1 → SZ | `common_rail`, `rail_decomposition` |
| Peer deltas | all pitchers ≥ 200 | PN-1 (both bases) | `peer_delta`, `peer_cohort` |
| z / p | counts | kernel `two_prop_z` | `premise_tests`, `split_tests` |
| Start medians | starters | first pitcher per half-inning side → SZ | `start_distribution(_summary)` |
| Notebook table | as client | kernel verbatim | `notebook_reproduction` |

## 4 · Known-defect exposure

See `05` §2. O-18 is **new** and is registered as a repo-wide environmental defect.

## 5 · Privacy (privacy-watchdog) and tagging (data-tagger)

Public MLB performance data and published player identity only. No PII beyond that. **CLEAR.** Tag: *Internal,
restricted to baseball operations*; domain Pitching; subject area Command; data product membership `uc-pps-031`.
External publication blocked pending DPO review.

## 6 · Versioning (version-controller)

- `uc-pps-031` v1.0.0: initial.
- **O-18 is breaking for consumers**, but in the environment, not in this product: every zone KPI's 2026 values mean something slightly different from 2025's. A change notice is drafted in `07` §5 for other UC owners.
- Changing `BALL_FT`, the SZ boundary rules, or the ZC-1 rail source is a **breaking** change to SZ/ZC-1.
