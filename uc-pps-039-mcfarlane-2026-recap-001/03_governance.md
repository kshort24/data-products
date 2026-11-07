# 03 · Governance
Agents: `kpi-calculator` · `technical-lineage-builder` · `dq-rule-definer` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search before declaring anything new
| Candidate | Search | Hit | Decision |
|---|---|---|---|
| bullet-slider test | K52 BS-1 | found (LHP-bound) | **BS-1r** generalization (hand passed in), non-breaking |
| fastball velo × spin rank | UC #47 kernel (archetype grades, drift-adjusted, cohort) | found, different population and grain | **FO-1 new**: raw velo/spin rank, Phillies-game population, UC #47 floor |
| bridge / setup-to-closer usage | grep `bridge\|setup\|duran` across kernels + `03_*` | UC #43 bullpen script (tiers, not per-outing hand-off) | **BD-1 new** |
| stint ledger MLB/AAA | UC #26 Keller LHV, UC #43 | ad hoc per UC | **ST-1 new** (dated outing ledger, tiers separate) |
| first-N outings | none | 0 | **FN-1 new** |
| client-language copy rule | NC-1 (UC #61) governs numbers only | partial | **CL-1 new** |

## 1 · Inheritance (`technical-lineage-builder`)
`dp_uc63_kernel.py` (sha `c4c0eea4ead2…`) imports, never copies. `assert_lineage()` asserts 11 pins at every run: `dp_uc62_kernel.py 2adc6005…` →
`dp_uc53_kernel.py 03d7e380…` → `dp_uc52` → `dp_uc51` → `dp_uc50` / `dp_uc49` / `dp_uc48` / `dp_uc44_kernel.py` + `barrel_rate.py` + `cumulative_metric.py` + `phillies_dp/recap_viz.py e6c9436a…`.
The client's notebook functions (`nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`, `hard_hit_rate`, `lhb_pitch_mix`, `rhb_pitch_mix`, `fpsr`) are the K44 Section A transcriptions: same code, same numbers.

## 2 · New KPI specs (`kpi-calculator`; filed in the BID 00:52 ET, before code)
### FO-1 fastball outlier rank (provisional)
- **Plain language:** where a pitcher's average four-seam velocity and spin rank among right-handed four-seam seasons seen in Phillies games.
- **Population:** `pps ∪ pos`, `p_throws == R`, `pitch_type == FF`, `game_type ∉ {S, E}`, 2015–26, deduped on the pitch key; pitcher-seasons with ≥ 100 FF.
- **Formula:** KP-1 percentile and rank on mean `release_speed` and mean `release_spin_rate` (subject excluded from the pool); joint = count of pool seasons with velo ≥ his AND spin ≥ his.
- **Edge cases:** names from pitching-role rows only (EN-3); raw, not drift-adjusted (UC #47 drift-adjusts).
### BD-1 bridge-to-Duran outing (provisional)
- **Plain language:** an outing where he entered with the Phillies ahead and Jhoan Duran pitched later in the same game.
- **Formula:** `entry_lead = fld_score − bat_score` at his first pitch > 0 AND Duran's first `at_bat_number` in the game > his last. Regular season graded; postseason shown.
### ST-1 stint ledger · FN-1 first-N outings (provisional, descriptive)
ST-1: MLB (house log) and AAA (`lhvp26`) outings by date, consecutive same-tier runs = a stint. FN-1: first N MLB outings by date, postseason kept, S/E dropped.
### BS-1r (Section B)
K52 BS-1 with `hand` as an argument: pitcher-season mean |HB| ≤ 4.0 in and mean |IVB| ≤ 4.0 in, ≥ 50 SL.
### CL-1 client-language copy rule
The client's sentences are the commentary, verbatim, except where a receipt contradicts a word or digit; each such edit is registered (`CORR` in `dp_uc63_narrative.py`) with its HP row and marked †; typo fixes are listed as copy edits.

## 3 · Lineage (column level, abbreviated)
`events` → PA / AB / H / BB / K → BA, OBP, SLG, OPS, wOBA (2026 weights), K%, BB% · `description` → swings / whiffs → whiff; `+ zone` → chase ·
`launch_speed`, `type` → hard-hit · `launch_speed_angle` → barrel · `strikes`, `events` → putaway · `pitch_type`, `stand` → usage ·
`pfx_x/z × 12` → HB/IVB · `release_speed`, `release_spin_rate` → FO-1 · `bat_score`, `fld_score`, `post_*`, `at_bat_number` → BD-1 entry/exit state.

## 4 · Defects and findings
| ID | Finding | Effect | Action |
|---|---|---|---|
| EN-3 | `player_name` in batting-role rows is the hitter | FO-1 labelled an opponent "Harper, Bryce" on the first pass | names from pitching rows; DQ-16 |
| AB-1 | 1 automatic ball (9/27) inside the 333 | counted as a pitch and in-zone (D-7); vs-LHB usage sums to 99.4% | kept (client frame counts it); DQ-05/15 WARN |
| RK-3 | K44 `chase_rate` rounds rates to .001 before percentiles | chase percentile 74th (published) vs 75th (unrounded) | harness tolerance ±1; DPO escalation |
| CL-a | Client draft truncates rather than rounds (BB 2.6% → "2%", HH 41.9% → "41%", barrel 9.7% → "9%") | three subtitle digits | registered corrections |

## 5 · Privacy (`privacy-watchdog`) and tags (`data-tagger`)
Public MLB performance data of public figures; no PII, no health data (no injury claim made). Carry-ins are public news. **Clear for external publish.**
Tags: domain `baseball.pitching`, subject area `player-recap`, sensitivity `public`, product `uc-pps-039`.

## 6 · Versioning (`version-controller`)
v1.0.0. A change to any BID bar, CL-1 correction, or FO-1/BD-1 definition after publish is **breaking**. A refreshed house log past 2026-10-01 is v1.1.0.
