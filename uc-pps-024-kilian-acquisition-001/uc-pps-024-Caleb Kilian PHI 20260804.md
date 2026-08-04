```yml
# Identity
name: Caleb Kilian Acquisition Read 20260804 PHI
id: uc-pps-024-Caleb Kilian PHI 20260804
description: >
  Trade-deadline acquisition onboarding for RHP Caleb Kilian, the newly acquired
  Phillies reliever with the least MLB history. Sizes what the 2026 starter-to-reliever
  conversion actually changed, separates contact avoidance from contact management,
  characterises his approach against left- and right-handed hitters, and turns the
  result into three sets of actions — pitching department, battery, and manager.
  Deep-dive angles: the reverse platoon split, and the backed-up slider that carries
  three of his five home runs.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — Ready for DPO Sign-off
priority: High

# People
personas: Manager (Don Mattingly), Pitching Coach / Department, Catchers, Pitcher, Pitching Analyst
owner: Kellen Short

# Relationships
parent_use_case: >
  UC3 (Luzardo deep dive) -> UC8 (Nola vs WAS, canonical flat-file) ->
  UC11 (Rangel, multi-level evidence) -> UC29 (Painter, self-scout variant) -> THIS
sub_use_cases: []
sibling_use_cases: >
  Remaining 2026 deadline acquisitions — this UC is the template for the cohort

# Metadata
created: 2026-08-04
last_updated: 2026-08-04
ledger_uc: 30
build_artifact: dp_uc29_kilian_acquisition_read.py
governance_trail: data-products/uc-pps-024-kilian-acquisition-001/00_ .. 07_
verification: dp_uc29_verification.py — 205/205 PASS

# Data References
data_sources:
  - data/opponents/kilian.parquet   # entity lock pitcher == 668873
entity_lock: pitcher == 668873
kpis:
  locked_inherited: [get_stats/nresults, whiff_rate, chase_rate, putaway_rate,
                     fpsr, hard_hit_rate, csw_rate]
  inherited_hardened: [xwobacon]                       # BIP-only, from uc-pps-021 O1
  new: [Slider Finish Rate, Fastball Elevation Rate, Role Conversion Delta]
data_domains: [At-Bat Outcomes, Batted Ball Profile, Pitch Profile, Pitch Outcomes,
               Strike Zone, Game State]
publish_scope: Internal only
```

# Acquisition Read — Caleb Kilian (RHP)

> **Document status:** deliverable `dp_uc29_kilian_acquisition_read_report.pdf` (9pp) ·
> governance trail `00_`–`07_` in this folder · receipts `out/dp_uc29_*.csv` (19) + 4 figures ·
> independent verification `dp_uc29_verification.py` — **205/205 PASS**

---

## Business Context

### Problem Statement

We just acquired five players at the deadline, and we're going to have to make decisions about all of them before we really know any of them. Kilian is first up because he has the least history to work through — a Cubs starting prospect who never stuck, no big-league time at all in 2025, and then a full season out of the bullpen for a Giants team that lost a lot of games in front of him.

That last part is the trap. A middle reliever on a bad team accumulates innings that look like closer innings and aren't. I don't want the ninth-inning appearance count doing the talking. I want to know what the conversion actually bought us, whether the underlying indicators back up the surface numbers, and then three specific things: what the pitching department should work on the first week they have him, what the catchers should be calling, and how Mattingly should slot him.

Nobody in this organization has ever worked with him. This is the first read, and it needs to be honest about how much of it is a small sample.

### Business Questions — Answered

**1. What do his top-line results say?**
2026 as a reliever: **193 PA, 27.5% K, 9.3% BB, .231 BA against, 5 HR** over 45 outings. As a starter (2022-24, 8 starts, 138 PA): 15.2% K, 13.8% BB, .315 BA. The strikeout rate nearly doubled and the walk rate fell by a third.

**2. What do the underlying indicators say?**
They corroborate the surface, with one important qualification. **All ten tracked process KPIs improved**: whiff 17.7→28.8%, chase 21.1→32.0%, putaway 13.6→24.3%, first-pitch strikes 58.7→63.2%, hard-hit 46.2→35.6%, exit velocity 89.8→85.3 mph. The four-seamer gained **+2.9 mph**. But **xwOBAcon moved only .370→.346** — when he is squared up, the ball still leaves at a damage rate. *He bought contact avoidance, not contact management.*

**3. What should we expect?**
Stability, not further improvement, absent intervention. Velocity is flat across all five months (96.5-97.4) and holds in second innings (96.8→96.2). Whiff and chase rates are flat month to month. There is no trend to extrapolate in either direction — which makes the two location fixes below the realistic source of upside.

**4. How does he approach left- and right-handed hitters?**
**Vs LHH (110 PA):** essentially two pitches — four-seam 52.7%, knuckle curve 31.7%. Fastball up, curve to finish (36.6% with two strikes). **Zero home runs allowed, 31.5% hard-hit, .309 xwOBAcon.**
**Vs RHH (83 PA):** a genuine four-pitch mix — sinker early, slider when ahead, curve/slider with two strikes. **37.5% whiff and 31.3% K — and all five home runs, 42.2% hard-hit, .410 xwOBAcon.**
**He is a reverse-platoon reliever.** The strikeouts point one way and the damage points the other.

**5. Where does the damage come from?**
One pitch and one location. Three of five home runs are sliders to RHH that **backed up to the arm side** instead of finishing glove-side. Sliders that finished: 32 thrown, 57.1% whiff, 78.4 mph, **zero** HR. Sliders that backed up: 15 thrown, 30.0% whiff, 98.4 mph, **three** HR. A quarter of his sliders go to the wrong side, and that quarter is the whole problem. Secondary leak: the four-seamer in the lower third yields 94-98 mph contact against both hands.

### Actions

**Pitching department**
1. Fix the slider finish — Slider Finish Rate from 52.5% glove-side toward **70%+**, arm-side under 15%.
2. Re-weight vs RHH — knuckle curve up from 15.1% (it whiffs at 66.7%), slider down from 20.0% until the finish holds.
3. Retire the sinker vs LHH — 7.8% usage, 50% hard-hit, 88.3 mph. Redundant with a better fastball.
4. Leave the velocity alone. It is stable and there is no conditioning problem.

**Battery**
*One rule: fastballs up, breaking balls glove-side, never let the slider drift arm-side to a righty.*
Vs LHH — four-seam elevated, knuckle curve to finish, shelve the sinker.
Vs RHH — sinker to open, **knuckle curve as the out pitch (not the slider)**, slider only glove-side and below the belt, never the fastball to the lower third.

**Manager**
1. **One inning, four batters, then get him** — whiff 30.3%→26.6% and exit velocity 84.3→88.1 mph on batters 4-5, with velocity unchanged. Familiarity, not fatigue.
2. **Point him at left-handed stretches** — 110 PA vs LHH without a home run.
3. **Not a one-run ninth yet** — the right-handed home-run exposure is a one-swing risk. He was never San Francisco's closer (13 of 20 ninth-inning entries came up 2+; only 2 with a one-run lead).
4. **Available often, can go two** — 8 outings on one day's rest, 14 on two, 8 two-inning appearances.

---

## Data Specification (summary)

**Grain:** one row per pitch. **Entity key:** `pitcher == 668873` (never a name filter).
**Source:** `data/opponents/kilian.parquet`, regular season only, deduped on `(game_pk, at_bat_number, pitch_number)`. 1,271 rows.

**Era tiers — never blended.** Current = 2026 SF relief (736 pitches / 193 PA / 45 outings). Prior = 2022-24 CHC starting (535 / 138 / 8). The prior tier sizes the conversion; it does not describe the pitcher acquired.

**Three populations, declared per metric:** FULL (736, PA outcomes) · TRACKED (728, usage + location — excludes 8 `automatic_ball` pitch-timer rows) · BIP (118, contact quality).

**New KPIs:** Slider Finish Rate, Fastball Elevation Rate, Role Conversion Delta — all specified in `02_engineering_design.md` §2.2 before use, all returned to the DPO as glossary-promotion candidates.

**Known gaps (all non-blocking, all disclosed):**
- **2025 is a true gap** — no MLB service, no MiLB cache. It sits *inside* the conversion window. Largest interpretive limitation in the product.
- **No opponent dimension** — no assigned role, never pitched for the org. Descoped with a follow-on trigger.
- **No Phillies rows** — by construction.
- **Prior era is 8 starts** across three seasons; clears 100 BF on a technicality.
- **Platoon splits are directional** (110 / 83 PA). Re-test at 150 PA.
- **ERA/IP/saves unavailable** — no built `gms_AI` for this pitcher.

**Open items:** O1 (`xwobacon` promotion, carried from uc-pps-021) · **O2** (locked `in_zone_rate` counts null zone as in-zone — new) · **O3** (`launch_speed` populated on foul balls — new) · O4 (platoon split directional).

**Closure step:** re-read at 150 PA in Phillies uniform — re-test the platoon split and Slider Finish Rate against the 70% target.
