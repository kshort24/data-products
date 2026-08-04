# 01 — Strategy & Intake

**Layer 1 — Intake & Discovery** · UC #31 · `uc-pps-025` · build `dp_uc30`
**Agents:** `use-case-validator` → `source-system-profiler` → `domain-steward-proxy`
**Gate result:** ✅ **GO** — 0 blocking, 6 non-blocking gaps

---

## 1.1 `use-case-validator` — intake gap report

The incoming request was written prose from the human DPO. Decomposed into six answerable questions:

| # | Question as asked | Answerable? | Evidence route |
|---|---|---|---|
| Q1 | Top-line results | ✅ | `nresults` on the era partition |
| Q2 | Underlying indicators, and expectations from them | ✅ | whiff / chase / CSW / zone / hard-hit / xwOBAcon vs results |
| Q3 | Approach vs LHH and vs RHH | ✅ | pitch × hand × count matrices |
| Q4 | Release point benchmarked against historical Phillies LHPs | ✅ *with a proxy* | `phils_2015..2026`, LHP filter — see G3 |
| Q5 | Does it change how batters track the ball? | ⚠️ **partially** | geometric answer is direct; the *tracking* answer leans on 32/61-whiff miss-distance samples — see G4 |
| Q6 | Actions for pitching dept / battery / manager | ✅ | derived from Q2–Q5 plus deployment log |

### Gap register

| ID | Gap | Class | Resolution |
|---|---|---|---|
| **G1** | **Zero Phillies rows.** Raley has never thrown a pitch for the organization; the cache is Mets through 2026-08-02 | **Non-blocking** | Reframe deliverable as an intake dossier. No opponent dimension — there is no next opponent because no role is assigned. Follow-on UC triggered when a role exists |
| **G2** | **2024 is a partial season (119 pitches, 8 outings) — Tommy John surgery** | **Non-blocking** | Drove the era design. Boundary derived from data: last outing 2024-04-19, return 2025-07-19. Rehab interval is a true gap, asserted as 0 rows |
| **G3** | **Native `arm_angle` exists in `phils_*.parquet` only from 2025.** The requested benchmark spans 2015–2026 | **Non-blocking** | Derive Release Slot Angle from `release_pos_x` / `release_pos_z` (populated for the full span), calibrate against native `arm_angle` on the 10-pitcher overlap, publish r and residuals, label it a proxy everywhere. **Escalated to DPO as a method decision; approved** |
| **G4** | **Q5 asks a perceptual question of a pitch-tracking dataset.** "How batters track the ball" is not a measured field | **Non-blocking** | Answer in two labelled layers: (a) *geometry* — Sightline Offset, directly measured and strong; (b) *behavioural proxies* — miss distance, swing length, bat speed, contact quality. Layer (b) samples are small (32 LHH / 61 RHH whiffs) and are labelled corroborating, not conclusive |
| **G5** | **KBO 2015–2019** is outside Statcast and outside the repo | **Non-blocking** | Recorded gap, never a zero. Asserted: 0 pre-2020 rows claimed as MLB evidence |
| **G6** | **Bat-tracking fields begin 2023** | **Non-blocking** | Pre-TJ tracking row covers 222 of 1,450 swings. Comparisons labelled indicative |

**0 blocking gaps → GO.**

### Acceptance criteria agreed at intake

1. Every published rate carries its sample size inline.
2. Pre-TJ and post-TJ rates are never blended into a single figure.
3. The release-point claim is benchmarked against a defined population, not asserted.
4. Any proxy metric ships with its calibration against the thing it proxies.
5. Each of the three personas receives an actionable section, not a restatement of the analysis.
6. Every number in the report reconciles under an independent recompute.

---

## 1.2 `source-system-profiler` — fitness for purpose

### Subject

| Property | Value |
|---|---|
| File | `data/opponents/raley.parquet` |
| **Entity lock** | `pitcher == 548384` — **id, never a name filter** (the Nola / "Nolan Hoffman" contamination is the canonical failure) |
| Filters | `game_type == 'R'`; dedup on `(game_pk, at_bat_number, pitch_number)` |
| Rows after lock | **4,184** pitches |
| Window | 2020-07-24 → **2026-08-02** (T-2 as of build) |
| Distinct pitcher ids / names / hands | 1 / 1 / L — **clean lock, no contamination** |
| Teams | CIN, HOU (2020–21), TB (2022), NYM (2023–26) |
| Age (`age_pit`) | 32 → **38** across the window |
| **Fitness** | **FIT** for the full ask, with the era split enforced |

### Distribution by season

| Season | Pitches | Outings | BF | Era tier | Team |
|---|---|---|---|---|---|
| 2020 | 336 | 21 | 84 | Pre-TJ | CIN/HOU |
| 2021 | 865 | 58 | 206 | Pre-TJ | HOU |
| 2022 | 846 | 60 | 219 | Pre-TJ | TB |
| 2023 | 996 | 66 | 236 | Pre-TJ | NYM |
| 2024 | 119 | 8 | 25 | Pre-TJ *(surgery)* | NYM |
| 2025 | 388 | 30 | 99 | Post-TJ *(return 7/19)* | NYM |
| 2026 | 634 | 45 | 170 | Post-TJ | NYM |

### Benchmark population

| Property | Value |
|---|---|
| Files | `data/phillies/phils_2015.parquet` … `phils_2026.parquet` |
| Filters | `phillies_role == 'pitching'` & `p_throws == 'L'` & `game_type == 'R'`, deduped, tracked pitches only |
| Inclusion threshold | **≥ 300 tracked pitches** (DPO decision) |
| **Population** | **28 pitchers**, 65,221 LHP pitches, 2015–2026 |
| Range | Milner (release side 3.83 ft, height 4.51) → Falter (0.91 ft, 5.73) |
| Raley's membership | **Excluded from the centroid.** He has never thrown a Phillies pitch; including him would be circular. He is *scored against* the population |
| **Fitness** | **FIT** for release geometry (`release_pos_x/z` populated 2015–2026). **PARTIAL** for arm angle — native field 2025–26 only → G3 |

### CDE completeness, post-TJ tier

| CDE | Coverage | Note |
|---|---|---|
| `release_pos_x` / `release_pos_z` / `release_extension` | 0.996 | critical — passes ≥0.95 |
| `stand`, `description` | 1.000 | critical |
| `pitch_name`, `zone`, `plate_x`, `plate_z` | 0.996 | 18 untracked rows quarantined |
| `pfx_x`, `pfx_z`, `release_speed` | 0.996 | |
| `release_spin_rate` | 0.988 | |
| `arm_angle` | 0.968 | native field present for Raley across all seasons |
| `estimated_woba_using_speedangle` | 0.260 | **expected** — exists on balls in play. Drives the `xwobacon` BIP-only rule |
| `launch_speed` | 0.336 | expected — batted balls only |

**18 untracked rows** (automatic balls / pitch-timer violations) carry null `pitch_name`, `zone` and location. Quarantined from usage-share and location work, retained for plate-appearance outcomes — inherited from UC#30 open item O2.

### Coordinate convention — established, not assumed

Every sightline claim depends on knowing which sign of `release_pos_x` is the left-handed hitter's side. Confirmed two independent ways and asserted in the DQ scorecard:

| Test | Result |
|---|---|
| Phillies **LHP** mean `release_pos_x` | **+2.072** (positive) |
| Phillies **RHP** mean `release_pos_x` | **−2.079** (negative) |
| Raley HBP `plate_x` vs **LHH** | **+1.915** (positive) |
| Raley HBP `plate_x` vs **RHH** | **−2.198** (negative) |

→ **Positive x = the side left-handed hitters stand on = the side a left-hander's arm occupies.** Both tests agree. A left-handed pitcher and a left-handed hitter occupy the same side of the field, which is precisely why a wide-slot lefty is a problem for lefties.

---

## 1.3 `domain-steward-proxy` — domain context

Standing in for a human pitching-domain steward. Surfaced from repo history and prior UCs:

* **Tommy John is a hard analytical boundary, not a soft one.** Velocity, slot and pitch shape all move across it. Prior UCs in this repo (Painter, UC#29) already established the never-blend rule for return-from-injury tiers; this UC applies the same discipline with a data-derived boundary.
* **A 38-year-old reliever's post-surgery profile is expected to trade whiffs for control.** Observing that trade is not a red flag; failing to note its fragility would be.
* **Sweeper shape is the sensitive metric for this pitcher archetype.** A low-slot lefty's sweeper is his carry pitch; small IVB changes move whiff rate a lot. Flagged pre-build as the thing most likely to explain any process change — and it was.
* **`arm_angle` is a newer Statcast field.** Its absence from older repo files is a cache-vintage artifact, not a data error. Do not treat pre-2025 nulls as missing data to be imputed.
* **The opponent-folder cache is the right source for a non-Phillie.** Entity lock and dedup discipline are unchanged; only the source path differs. Inherited from UC#30.
* **`xwobacon` supersedes `get_stats.xwoba`** (uc-pps-021 open item O1). The pitch-level column averages over non-BIP rows and is quarantined.

**No business meaning was inferred at this layer.** Where a term needed a definition it was routed to `business-glossary-agent` (file 03).
