# 04 — Architecture & KPI Specifications
## `uc-pos-007` / `dp_uc27` · Layer 2 · Agents: `data-architect`, `kpi-calculator`, `eda-agent`

---

## 1. Model blueprint

### 1.1 Grain

**One row per tracked pitch.** Every published table is an aggregation of that single grain. No
table in this product joins two fact grains, so no fan-out is possible below the aggregation step.

### 1.2 Topology

```
                    data/phillies/phils_2015..2026.parquet
                      └─ filter phillies_role == 'batting'
                      └─ filter batter ∈ ROSTER (11 MLBAM ids)
                                     │
    data/opponents/*.parquet  ───────┤      (30 files: hitter pulls, team pulls,
      └─ filter batter ∈ ROSTER      │       opposing-pitcher pulls, MiLB frames)
                                     ▼
                        ┌────────────────────────┐
                        │  UNION (concat)        │   150,421 rows
                        └────────────────────────┘
                                     │
                        drop_duplicates(game_pk, at_bat_number, pitch_number)
                                     │
                        left join  wOBA and FIP Constants.csv
                          on game_year == Season      (dimension, 1:1)
                                     │
                        ┌────────────────────────┐
                        │  GOVERNANCE FILTERS    │   4 rules, ordered
                        │  1 game_type == 'R'    │   −6,439
                        │  2 COMPETITION_LEVEL   │   −7,172
                        │  3 venue integrity     │   −44
                        │  4 p_throws == 'R'     │   −39,531
                        └────────────────────────┘
                                     │
                                 97,235 rows
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
      COHORT A (all rows)   COHORT B (visitors)     COHORT C (Alcantara)
      venue ∈ {MIA, other}  ¬miami_home_club        pitcher == 645261
      1,901 / 22,691 PA     1,038 / 22,691 PA       163 / 146 PA
```

### 1.3 Design decisions and the reasons for them

| Decision | Rationale |
|---|---|
| **Union then dedup**, not "pick one source per hitter" | No single source covers a full career. `phils_*` has only Phillies-era rows; hitter parquets stop when the player joined Philadelphia; team and pitcher pulls carry fragments. Union is the only complete option, and the dedup key is exact |
| **Dedup on `(game_pk, at_bat_number, pitch_number)`, keep first** | Statcast's natural pitch key. Proven sufficient and necessary in `05_ §2` — after dedup, zero duplicate keys remain, and 6–18% of Miami rows per hitter were removed |
| **Filters ordered cheapest-first is *not* used**; order is semantic | The exclusion audit reports rows removed *by each rule in sequence*, so the counts are interpretable as "what this rule uniquely removed." Reordering would change the attribution but not the final row set |
| **Three cohort frames rather than one with a flag column** | The visitors-only cohort is a different population, not a filter on the same population. Publishing it as a peer frame forces every consumer to see both numbers |
| **No league-wide baseline** | Not available locally. Roster-as-its-own-baseline is stated as the benchmark rather than implied |
| **No bat-tracking metrics** | `bat_speed` / `attack_angle` are Statcast 2024+. Including them would fracture a 2015–2026 cohort |

---

## 2. Locked KPI inventory — inherited verbatim

Copied without modification from `dp_uc24` (`uc-pos-006`), which inherited from `dp_uc20` and
*Baseball Functions.ipynb*. Governance principle 2: these were **not** re-derived.

| KPI | Formula | Grain | Population |
|---|---|---|---|
| `plate_apps` | count of `events ∉ {null, pickoff_1b}` | any | all rows |
| `at_bats` | PA minus BB, IBB, HBP, SF, SH | any | all rows |
| `ba` | hits ÷ at_bats | any | all rows |
| `obp` | (hits + walks + hbp) ÷ plate_apps | any | all rows |
| `slg` | (1B + 2·2B + 3·3B + 4·HR) ÷ at_bats | any | all rows |
| `ops` | obp + slg | any | all rows |
| `woba` | Σ(wBB, wHBP, w1B, w2B, w3B, wHR) ÷ plate_apps | any | all rows, season weights |
| `xwoba` | mean of `estimated_woba_using_speedangle` | any | rows where populated |
| `iso` | slg − ba | any | all rows |
| `krate` | strikeouts ÷ plate_apps | any | all rows |
| `bbrate` | walks ÷ plate_apps | any | all rows |
| `hr_rate` | home runs ÷ plate_apps | any | all rows |
| `hard_hit_rate` | count(`launch_speed >= 95`) ÷ BIP | any | `type == 'X'` |
| `barrel_rate` | count(`launch_speed_angle == 6`) ÷ BIP | any | `type == 'X'` |
| `ev90` | `launch_speed.quantile(0.90)` | any | `type == 'X'` |
| `chase_rate` | swings on `zone > 9` ÷ pitches with `zone > 9` | any | all rows |
| `whiff_rate` | whiffs ÷ swings | any | all rows |
| `bb_type` shares | count per `bb_type` ÷ BIP | any | `type == 'X'` |

`pitches_per_pa` = total pitches ÷ plate_apps, taken from the requester's snippet. Not a new KPI —
an arithmetic convenience — but its limitation under a handedness filter is registered as DS-4.

**Denominator consistency is a certification requirement**, not a convention: `hard_hit_rate`,
`barrel_rate`, `ev90` and `bb_type` shares all use the identical `df[df.type == 'X']` population
counted the same way. Tested by DQ-14.

---

## 3. New KPI specifications — PROVISIONAL

### VD-1 · Venue Delta

**Plain language.** For any rate statistic, the signed difference between a hitter's value at
loanDepot park and the same hitter's value at every other MLB park. Positive means the hitter is
better in Miami.

**Formula.**

```
VD-1(k, h) = KPI_k(h, venue = 'loanDepot park') − KPI_k(h, venue = 'All other MLB parks')
```

| Attribute | Value |
|---|---|
| Grain | One row per hitter |
| Applied to | `ops`, `woba`, `xwoba`, `ba`, `obp`, `slg`, `iso`, `krate`, `bbrate`, `hard_hit_rate`, `barrel_rate`, `ev90`, `pitches_per_pa`, `chase_rate` |
| Population | Governed frame (all four filters applied) |
| Qualification gate | `pa_miami >= 40` **and** `pa_other >= 100`. Hitters below the gate are computed, flagged `qualified == False`, and excluded from every pooled statement |
| Null / edge handling | A hitter with zero PA in either cohort produces **no row** (set intersection, not outer join). Rincones Jr. therefore does not appear in `venue_delta.csv` |
| Zero-BIP guard | Inherited from `barrel_rate` / `hard_hit_rate`; a cohort with no balls in play yields `NaN`, not a divide-by-zero |
| Receipt | `out/dp_uc27_venue_delta.csv` |
| **Provisional because** | The PA gate is a house convention (the standard batter gate is 50 PA; 40 was used for Miami because venue cohorts are structurally smaller). The DPO must set the gate explicitly before this term is inheritable |

### VD-2 · Venue Signal Class

**Plain language.** A hitter's venue split is only interesting if the *results* and the *contact
quality* move together. VD-2 compares the direction of the wOBA delta against the direction of a
three-part contact-quality composite and names the four possible combinations, so a loud results
split with a silent process split is labelled as noise rather than read as a finding.

**Formula.**

```
process_composite(h) = mean( VD-1(hard_hit_rate, h) / 0.060 ,
                             VD-1(barrel_rate,   h) / 0.035 ,
                             VD-1(ev90,          h) / 2.500 )

results_delta(h)     = VD-1(woba, h)
```

| Condition | Class |
|---|---|
| not qualified (VD-1 gate) | `Insufficient sample` |
| \|results\| < .020 **and** \|composite\| < 0.30 | `Neutral` |
| results > 0 **and** composite > 0 | `Miami boost — results and process agree` |
| results < 0 **and** composite < 0 | `Miami drag — results and process agree` |
| results > 0 **and** composite ≤ 0 | `Results-only lift — treat as noise` |
| results < 0 **and** composite > 0 | `Process-only lift — under-rewarded in Miami` |

| Attribute | Value |
|---|---|
| Grain | One row per hitter |
| Divisors | `0.060` hard-hit, `0.035` barrel, `2.500` EV90 — approximate population dispersion, used to put three differently-scaled metrics on a comparable footing so EV90's mph units do not dominate |
| Null handling | `np.nanmean` — a hitter missing one process component is classified on the remaining two |
| Receipt | `out/dp_uc27_venue_delta.csv`, column `venue_signal_class`; visualised in `fig2` |
| **Provisional because** | Both the divisors and the boundaries are judgement calls with no fitted basis. Borderline hitters (Harper at composite +0.225, Turner at −0.208) would reclassify under modest changes. The `business-glossary-agent` recommendation is to hold VD-2 pending a dispersion study across more than one roster |

**Banner requirement.** Wherever VD-1 or VD-2 appears in a consumer-facing artifact it must carry
the provisional marking. Enforced in the reader report (§7 caveats) and the persona card footer.

---

## 4. EDA findings that shaped the design

`eda-agent` ran distribution, correlation and outlier passes on the governed frame before the
architecture was frozen. Three findings changed the build:

1. **Variance decomposition put tenure above venue.** Splitting the Miami cohort by
   `VENUE_TENURE_CONTEXT` explained more of the wOBA gap than the venue split itself: the home-club
   sub-cohort posts `.281` wOBA / `.326` xwOBA on 863 PA against `.337` / `.391` for the
   visiting-club sub-cohort on 1,038 PA and `.345` / `.376` for the road baseline. This promoted
   CDE-3 from a nice-to-have to a required cohort frame and became the report's spine.
2. **The results/expected divergence is systematic, not idiosyncratic.** Pooled, wOBA falls 34
   points in Miami while xwOBA falls 14. Per hitter, two of the eight qualified hitters
   (Harper, Schwarber) post a positive process delta against a negative results delta, and a third
   (Turner) posts a `−.046` results delta against a `−.004` expected delta. That asymmetry is what
   VD-2 exists to name.
3. **The apparent park-era effect is collinear with tenure.** Realmuto's 783 home-club PA all sit
   in the pre-2020 bucket, and removing them collapses the era difference from 24 points of wOBA to
   9. The era split is still published — with the collapse stated — so that the hypothesis is
   closed rather than left open.

---

## 5. Acceptance criteria

| # | Criterion | Met |
|---|---|---|
| A-1 | The requester's KPI panel (`plate_apps`, `pitches_per_pa`, `ba/obp/slg/ops`, `woba`, `hard_hit_rate`, `barrel_rate`, `ev90`) is reproduced at hitter × venue grain | Yes — `venue_split.csv` |
| A-2 | All 11 named hitters are represented, or their absence is explained | Yes — Rincones Jr. has zero Miami PA and is named in the report |
| A-3 | MiLB rows are excluded and the exclusion is quantified | Yes — DQ-05, `01_ §3.3` |
| A-4 | The Alcantara lens is delivered as a second perspective within the same UC | Yes — report §3 |
| A-5 | Players to watch, persona actions and trends are identified | Yes — report §4, §5, §6 |
| A-6 | PDF deliverable | Yes — 9-page branded report + 1-page persona card |
| A-7 | Every published number is recomputed independently and reconciles | Yes — 256/256, `dp_uc27_verification.py` |
| A-8 | No number appears in the report that the build did not compute this session | Yes |
