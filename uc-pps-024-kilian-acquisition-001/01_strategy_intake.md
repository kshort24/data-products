# 01 — Strategy & Intake

**Department:** Strategy & Intake · **Agents:** `use-case-validator`, `source-system-profiler`, `domain-steward-proxy`
**Layer 1 verdict:** ✅ **GO** — 0 blocking gaps, 5 non-blocking (all resolved by descope or disclosure)

---

## 1.1 `use-case-validator` — intake gap report

The incoming request was prose, not a structured use-case document. Validator reconstructed the contract and stress-tested it.

| # | Gap | Classification | Resolution |
|---|---|---|---|
| V1 | **No opponent named, no role assigned** | *Non-blocking (descope)* | The four consumer questions are development, battery and deployment questions. None requires an opponent. Opponent dimension formally **descoped** with a follow-on trigger: re-open once a role is assigned. Recorded so it reads as a decision, not an omission |
| V2 | **2025 season entirely absent** | *Non-blocking (disclosure)* | No MLB service in 2025; no Sacramento MiLB cache in this repo. Recorded as a **true gap** — never interpolated, never bridged. Escalated in the report as the single largest interpretive limitation, since an unobserved developmental season sits between the two eras being compared |
| V3 | **Prior era is 8 starts across 3 seasons** | *Non-blocking (threshold disclosure)* | 138 PA clears the 100-BF publish threshold on a technicality. Every use of the prior tier carries both denominators via the Role Conversion Delta KPI, which flags `prior_below_threshold` structurally |
| V4 | **"Top-line results" is ambiguous** — ERA/WHIP are not in the Statcast layer | *Non-blocking (scope)* | This repo has no `gms_AI` built for Kilian and no earned-run ledger. Top-line is delivered as **Statcast-derivable outcomes** (K%, BB%, BA, wOBA-family, HR) and the absence of ERA/IP/saves is disclosed. Consistent with the `uc-pps-007` note that win/runs KPIs need a built `gms_AI` |
| V5 | **Reverse platoon split drives the deployment recommendation but rests on 83 PA** | *Non-blocking (sample discipline)* | Every platoon line prints its PA and BIP. The recommendation is framed as a strong prior with an explicit re-test trigger at 150 PA (→ O4) |

**Feasibility:** ✅ all four consumer questions answerable from the supplied cache.
**Internal consistency:** ✅ no contradictory requirements.
**Verdict: GO.**

---

## 1.2 `source-system-profiler` — fitness for purpose

**Entity lock:** `pitcher == 668873` (Caleb Kilian, MLBAM). **Name filters were not used at any point** — this is the canonical failure mode from the Nola / "Nolan Hoffman" contamination, and the lock is asserted in both the build and the verification script.

| Source | Tier | Rows after filter | Window | Fitness |
|---|---|---|---|---|
| `data/opponents/kilian.parquet` | MLB — current (2026 SF, relief) | 736 pitches / 193 PA / 45 outings | 2026-03-27 .. 2026-08-01 | **FIT** — full Hawk-Eye ≥98%; batted-ball quality BIP-complete |
| `data/opponents/kilian.parquet` | MLB — prior (2022-24 CHC, starting) | 535 pitches / 138 PA / 8 outings | 2022-06-04 .. 2024-09-24 | **FIT, directional** — clears 100 BF but only 8 outings |
| *(none)* | 2025 MiLB (Sacramento) | 0 | n/a | **ABSENT** — true gap, no supporting tier |
| *(none)* | Phillies rows for 668873 | 0 | n/a | **ABSENT** — never pitched for the org |

**Freshness:** cache max `game_date` = **2026-08-01**, three days before the report date. T-3, disclosed in the report header.

**Field-level fitness (2026 tier, 736 rows):**

| Field class | Fields | Populated | Verdict |
|---|---|---|---|
| Hawk-Eye tracking | `release_speed`, `release_spin_rate`, `pfx_x/z`, `plate_x/z`, `sz_top/bot`, `release_extension`, `arm_angle`, `zone` | 98.9% | **FIT** — the 1.1% shortfall is exactly the 8 untracked rows below |
| Contact quality | `launch_speed`, `launch_angle`, `estimated_woba_using_speedangle` | **100% of balls in play** | **FIT on BIP** — 31% of all pitches, which is the expected BIP rate, not a defect |
| Outcome | `events`, `description`, `type`, `stand` | `events` 26% (PA-terminal by design); rest 100% | **FIT** |
| Swing-side | `bat_speed`, `swing_length`, `attack_angle` | 46% | **EXCLUDED** from every published KPI |

### The three source findings that changed the build

**1. Eight untracked `automatic_ball` rows.** All 8 null-tracking rows in the 2026 tier are pitch-timer violations — no ball is thrown, so pitch type, zone and location are null. They are legitimate BALL events for plate-appearance outcomes but are **not pitches** for usage share or location analysis. The profiler's call: define a **tracked-pitch population** (`pitch_name.notna()`, n=728) for all pitch-mix and location denominators, retain the full population (n=736) for PA outcomes. This is asserted in the DQ scorecard and independently re-checked in verification (D33-D35).

**2. `launch_speed` is populated on foul balls.** 114 of 736 rows carry an exit velocity with `type != 'X'`. Any mean taken without the `type=='X'` filter reads several mph low — fouls are systematically weaker contact. This is a **trap the repo did not previously have documented**, and it caught an early draft of this report's slider table (86.8 mph published as 80.8). → O3.

**3. `zone` nulls flow into the locked in-zone rate.** The inherited `chase_rate()` computes in-zone as `(pitches − ooz)/pitches` with `ooz = zone > 9`; a null zone is not `> 9`, so untracked rows land in the in-zone numerator. → O2.

---

## 1.3 `domain-steward-proxy` — domain context

No human domain steward was available; the proxy supplied the baseball-domain rules that shape interpretation. **All of these are context, not findings — none of them generated a published number.**

| Context | Bearing on the analysis |
|---|---|
| **Starter→reliever conversion is expected to add velocity and subtract arsenal.** One inning, max effort, fewer pitches to command | This is why the era comparison is framed as *role conversion*, not *development*. The +2.9 mph and the drop from six pitches to four are the expected signature — the report says so rather than presenting them as discovery |
| **A reliever's platoon split is a deployment input in a way a starter's is not.** A manager can choose the hitters | Elevates the platoon section from descriptive to actionable, and is why the reverse split leads the deployment recommendation |
| **Three-batter minimum rule** | Bounds the "four batters, then get him" recommendation — the manager cannot pull him after one regardless of matchup |
| **A slider that "backs up" is an execution miss, not a design flaw** — the pitch stays on the arm side instead of finishing glove-side, arriving flat and centred | Direct motivation for the Slider Finish Rate KPI. Without this domain rule, glove/arm-side location is just a split; with it, it is a coachable execution metric |
| **A high-IVB four-seamer plays at the top of the zone** — its value comes from arriving above the barrel plane | Motivates Fastball Elevation Rate and makes the lower-third exit-velocity result interpretable rather than incidental |
| **2026 Giants context: a poor team runs its bullpen differently** — low-leverage innings are plentiful, high-leverage reps are scarce | Explains why 20 ninth-inning entries do **not** mean "closer." The score-state breakdown was added specifically because of this caution |

**Steward-proxy caveat:** none of the above is sourced from a written Phillies domain document — it is general baseball-domain knowledge supplied in the absence of a human steward. Any of it that hardens into a repeated modelling assumption should be ratified by a human and moved into the glossary.
