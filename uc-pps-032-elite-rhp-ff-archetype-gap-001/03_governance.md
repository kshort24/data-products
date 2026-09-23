# 03 · Governance — `uc-pps-032`

Agents: `business-glossary-agent` · `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search (before anything was declared new)

```
grep -rn  "ff_elite|elite_ff|elite_stuff"        MLB/  data-products/  contract/   → 0 hits
grep -rni "archetype"                            → uc-pos-003/009/011 (hitter "archetype" labels, prose only) — no function, no term
grep -rn  "benchmark_population|scouting_grade"  → dp_uc44_kernel.py (SG-1/SG-2) — INHERITED
grep -rn  "rv100|run_value_per_100"              → 0 hits
grep -rn  "delta_run_exp"                        → dp_uc4 / dp_uc5 (defensive run-saving, batting-team POV) — near-miss, different grain
grep -rn  "season_adjust|trend_adjust"           → 0 hits
grep -rn  "ivb|induced_vertical"                 → dp_uc28 / dp_uc44 `ivb_in` (= pfx_z × 12) — name REUSED
ls data-products | grep -i "bowlan|duran|wheeler|painter|mcfarlane|dominguez"
                                                 → uc-pps-018 (Duran), uc-pps-020 (Wheeler), uc-pps-023/030 (Painter)
```

**Prior-subject reuse:** Duran's 2026 four-seam was last graded by eye on the client's 9/17 index card ("70 FF");
Painter's four-seam by SG-4 in uc-pps-030 ("grades 60 on velocity and 70 on run, and 40 as a pitch") — this UC's
results grade of 40 agrees with that independent read.

## 1 · Business glossary (14 terms)

| Term | Definition | Status | Note |
|---|---|---|---|
| **Archetype** | A declared pitch × hand × era with a shape axis, a results axis and a bar (AF-1) | NEW · provisional | generalizes beyond this pilot |
| **Elite RHP Four-Seam (archetype)** | RHP four-seam, 2018–26, plus (≥60) on both shape and results | NEW · provisional | the pilot instance |
| **Shape grade** | Mean of velocity, IVB and spin 20–80 grades, rounded to 5 | NEW · provisional | the house word for what a pitch looks like (uc-pps-030 "shape") |
| **Results grade** | Mean of whiff-rate and RV/100 grades, rounded to 5 | NEW · provisional | |
| `ff_elite_shape_flag` | shape grade ≥ 60 | NEW · provisional | **replaces the DPO draft `ff_elite_stuff_flag`** |
| `ff_elite_stuff_flag` | — | **RETIRED ALIAS** | "Stuff grade" = whiff grade (SG-4). One word, one meaning |
| `ff_elite_results_flag` | results grade ≥ 60 | NEW · provisional | name as drafted by the DPO |
| `ff_elite_archetype_flag` | both flags | NEW · provisional | |
| **Elite-FF composite** | round5(mean(shape grade, results grade)); `efc_score` = unrounded, weight 0.5 | NEW · provisional | ranking uses the unrounded score |
| **Elite-Four-Seam Share (EFS)** | staff RHP four-seams thrown by archetype-flagged arms ÷ all staff RHP four-seams | NEW · provisional | staff-season grain |
| **Induced Vertical Break (IVB)** | `pfx_z` × 12, inches | EXISTING (dp_uc28/44 `ivb_in`) | aliases: ride, carry, vert (client) |
| **Run Value per 100** | −100 × mean(`delta_run_exp`) over the pitch | NEW · provisional | pitcher POV; sign flip documented |
| **Sampling Frame / Coverage** | where a pitcher-season's rows come from (PHI/VS_PHI/FILE/TEAM/INCIDENTAL); COMPLETE vs PARTIAL | NEW · provisional | |
| **Competition Level** | MLB iff home and away are both MLB clubs | PROMOTED (uc-pos-015 escalation E-4) | third UC to need it — **now a governed term** |

## 2 · KPI specifications (kpi-calculator)

**Inherited, unchanged:** SG-1 `scouting_grade_20_80`, SG-2 floors (100 population / 50 subject / 25 swings),
SG-3 `grade_divergence_flag`, SG-5 `grade_label`, `SWINGS`/`WHIFFS` — by import from `dp_uc44_kernel.py`,
sha256 `a2c11909…` pinned.

| ID | Object | Plain language | Formula / rule | Grain | Edge cases |
|---|---|---|---|---|---|
| **FR-1** | `house_pitch_universe` | The client's "my dataset", governed | phils ∪ nphl; level gate; phils-precedence dedup; FILE/TEAM > INCIDENTAL; `game_type=='R'` | pitch | batter-keyed files detected, not assumed |
| **NR-1** | `resolve_pitcher_names` | Name a pitcher only from rows that are about him | T1 keyed modal name → T2 `des` "by pitcher X" (trusted iff ≥97% folded agreement) → T3 logged identity → else `MLBAM <id>` | pitcher | accents folded (O-12) |
| **AF-1** | `ArchetypeSpec` | An archetype is data, not code | pitch, hand, era, shape[], results[], floors, bar | spec | unknown metric fails loudly |
| **AF-2** | `archetype_frame` | One row per pitcher-season of the pitch | counts, means, whiff (NaN if 0 swings), RV/100, frame, coverage, role (median outing ≥ 50 on non-incidental rows ⇒ SP) | pitcher-season | incidental outings excluded from role |
| **SG-6** | `season_trend_adjust` | Put every season on 2026's ruler | OLS value~year on population; **iff p < .05**: adj = value + slope × (2026 − year) | pitcher-season | adjust only what drifts |
| **SG-7a** | `stabilization_k` | Pitches until half signal | odd/even split-half r → Spearman-Brown r_full at n̄ → k = n̄(1−r)/r | metric | deterministic, no RNG |
| **SG-7b** | `stabilize` | Pull thin samples toward the population | x_s = μ + n/(n+k)·(x − μ); shrink iff reliability at the 50-FF subject floor < 0.90 | pitcher-season | NaN stays NaN |
| **AF-3** | `archetype_grades` | Grade, roll up, flag | SG-1 per metric vs population; axis = round5(mean); flags ≥ 60; composite; `efc_score` | pitcher-season | whiff ungraded < 25 swings; thin = n < 100 |
| **AF-4** | `weight_sensitivity` | The G9 control | re-rank at w ∈ {0, .25, .5, .75, 1} | subject set | publish all five ranks |
| **AF-5** | `elite_ff_share` | How much of the staff's four-seam is elite | Σn(flag) / Σn | staff-season | ungraded arms count in the denominator |
| **AF-6** | `needle_swap` | What adding him would change | V_role × (efc_c − efc_d)/T; V_role × (flag_c − flag_d)/T; d = lowest-efc staff arm of the role | candidate | observed candidate volume never used (sampling ≠ role) |
| **CB-1** | candidate evidence floor | Rank only on real evidence | RANKED ⇔ latest 2025–26 season ≥ 100 FF; else WATCH (50–99) | candidate | same bar as population membership |

## 3 · Technical lineage (column-level, published numbers)

| Published number | Lineage |
|---|---|
| Shape grade | `release_speed`, `pfx_z`, `release_spin_rate` → AF-2 mean → SG-6 (velo, spin only) → SG-1 vs 405 → mean → round5 |
| Results grade | `description` → SWINGS/WHIFFS → whiff → SG-7 (k=56.1 swings) ; `delta_run_exp` → ×−100 → SG-7 (k=1,083.6) → SG-1 → mean → round5 |
| EFS | `phils_2026` · `phillies_role=='pitching'` · `p_throws=='R'` · `pitch_type=='FF'` → count by pitcher × `ff_elite_archetype_flag` |
| Needle | EFS inputs + staff `role` (AF-2) + `efc_score` (AF-3) → AF-6 |
| Candidate board | U ∖ staff → 2025–26 → CB-1 → AF-3 `efc_score` |
| HP-1..6 | raw `phils_*` rows filtered by the client's own rules (month < 7; spin ≥ 1500; `pd.concat([pps,pos,nphl])` via `kellen_frame_raw`) |

## 4 · Defect exposure (known repo-wide defects read against this build)

| Defect | Exposed? | Why |
|---|---|---|
| D-1/D-2 `whiff_rate` inner join drops zero-whiff groups | **No** | AF-2 computes whiff with its own NaN-safe denominator; `whiff_rate` used only as a cross-check (family C, 5/5 agree) |
| D-7/O-13 NULL zone counted in-zone | **No** | zone not used |
| O-5 truncated PA | **No** | PA counts not published |
| O-8 untracked BIP as not-hard-hit | **No** | hard-hit not used |
| O-12 accent folding in names | **Yes → handled** | NR-1 folds before comparing; most raw disagreements were accents. The 5 that remain are suffixes (III, Jr.) and initials (A.J., Luis F., Jose A.) — the T2 regex stops at a period, so initial-bearing names can display truncated. Logged as NR-1 limitation L-1 |
| O-18 2026 zone rails | **No** | zone not used |
| **NEW O-23** `get_nphillies_data()` has no level gate and no cross-source dedup | **Yes** | FR-1 is the fix; upstream `mlb_data.py` untouched (breaking for existing notebooks) |
| **NEW O-24** batter-keyed team pulls make `player_name` the batter | **Yes** | NR-1; affects any notebook that names pitchers from those files |
| **NEW BC-1** brand-center validator reads `plotly_template` → `template` → `layout`; a bare `template` string masks the layout font | **Yes → worked around** | pass the full block as `plotly_template` |

## 5 · Privacy, tagging, versioning

- **Privacy (`privacy-watchdog`):** public MLB performance data; no PII beyond published player identity. **CLEAR.**
- **Tags (`data-tagger`):** Internal — Restricted · domain `pps` (scope note: external evaluation) · subject area
  *pitching / roster construction* · product `dp_uc47`. External publication **blocked**: a list of other
  clubs' pitchers ranked in a Phillies acquisition context should not leave the building.
- **Versioning (`version-controller`):** v1.0.0. **Breaking** if any of: population definition (era, floor,
  frame), axis membership, the 60 bar, or SG-6/SG-7 decision rules change. **Non-breaking:** a refreshed anchor
  with identical definitions → v1.1.0. The client's draft flag name is a retired alias, never a second column.

## 6 · Ratification path

| Object | Cheapest independent second use |
|---|---|
| SG-1 / SG-2 | **This UC** (second use after uc-pps-030) → recommend ratify (00 E-1) |
| AF-1…AF-6, CB-1 | A second archetype on the same engine — e.g. elite LHP sweeper — with no code change |
| FR-1, NR-1 | Any UC that uses `nphl` (the next opponent advance) |
| SG-6, SG-7 | Any multi-season grading UC; the k values should reproduce within ±20% |
