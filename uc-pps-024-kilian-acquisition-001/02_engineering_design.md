# 02 — Engineering (Design)

**Department:** Engineering · **Agents:** `data-architect`, `kpi-calculator`, `eda-agent`, `join-validator`
**Layer 2 verdict:** ✅ complete — model blueprint fixed, 3 new KPIs specified **before** any output was produced

---

## 2.1 `data-architect` — model blueprint

**Grain:** one row per pitch. **Entity key:** `pitcher = 668873`. **Natural key:** `(game_pk, at_bat_number, pitch_number)`.

**Single-source design.** Unusually for this line of UCs, there is exactly **one** physical source — `data/opponents/kilian.parquet`. There are no joins between domains, which removes an entire class of risk (fan-out, key drift, grain mismatch) that `join-validator` normally has to police.

### Population lattice

The design decision that carries this UC is that **three different denominators are correct for three different question types**, and mixing them is the defect mode.

```
kilian.parquet
  └─ entity lock: pitcher == 668873
     └─ game_type == 'R'
        └─ dedup (game_pk, at_bat_number, pitch_number)          n = 1,271
           ├─ ERA TIER: game_year == 2026        (relief)        n =   736   ← current
           └─ ERA TIER: game_year in 2022..2024  (starting)      n =   535   ← prior
                                                                   (never blended)

  Within an era tier, three populations:
    P1  FULL         all rows                       n = 736   → PA outcomes: K%, BB%, wOBA, HR
    P2  TRACKED      pitch_name.notna()             n = 728   → usage share, zone rate, location
    P3  BIP          type == 'X'                    n = 118   → exit velocity, hard-hit, xwOBAcon
```

**Rule:** every published rate declares which population it sits on. P1↔P2 differ by the 8 untracked `automatic_ball` rows; P2↔P3 differ by contact. The DQ scorecard asserts all three counts, and verification re-derives them independently.

**Era-tier never-blend rule** (inherited from UC#11's multi-level rule, adapted): the prior tier is always labelled and never pooled into a current-tier rate. It exists to *size the conversion*, not to describe the pitcher.

### Output tables

| Table | Grain | Population | Serves |
|---|---|---|---|
| `era_summary` | era_tier | P1 + P3 | Conversion headline |
| `season_log` | game_year | P1 + P3 | Season trend, 2025 gap made visible |
| `arsenal_by_era` / `arsenal_2026` | era_tier × pitch / pitch | P2 (+P3 for contact) | Arsenal reshape |
| `role_conversion_delta` | KPI | P1/P2/P3 per KPI | **NEW KPI** |
| `platoon` / `pitch_by_hand` | stand / stand × pitch | P1 + P3 | Approach by handedness |
| `count_usage` | stand × count state × pitch | P2 | Battery card |
| `slider_finish` | stand × horizontal side | P2 + P3 | **NEW KPI** |
| `fastball_elevation` | stand × vertical third | P2 + P3 | **NEW KPI** |
| `slider_vertical_half` | vertical half (RHH) | P2 + P3 | Battery card |
| `damage_log` | home run | P1 | Damage attribution |
| `outing_log` / `deployment` | game / entry inning × score state | P1 | Manager section |
| `batter_sequence` | batters-faced bucket | P1 + P3 | Leash |
| `monthly_arc` | month | P1 | Stability check |

---

## 2.2 `kpi-calculator` — KPI specifications

### Locked, inherited VERBATIM from `dp_uc28_painter_vs_orioles.py`

`get_stats`, `nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`, `hard_hit_rate`, `csw_rate` — copied byte-identical, not re-derived. **Not modified even where a defect was found** (see O2): the inheritance rule outranks the fix, so a strict variant is published alongside instead.

### Hardened, inherited from `uc-pps-021` (O1)

**`xwobacon`** — mean `estimated_woba_using_speedangle` over `type == 'X'` only. The locked `get_stats.xwoba` averages over all pitch rows and is contaminated; it is **quarantined and never published in this UC**. Applying this hardening changed the headline conversion story materially and honestly: the contaminated column showed a −.087 contact-quality improvement, the hardened one shows **−.024**. The report says so.

### NEW — specified before use, per governance principle 1

**NEW-1 · Slider Finish Rate (SFR)**

| Field | Spec |
|---|---|
| Plain language | Of the sliders he throws, what share actually finish to the glove side — and what happens on the ones that back up to the arm side instead? |
| Formula | `SFR = count(slider AND plate_x > 0.15) / count(slider AND plate_x notnull)`, with arm-side complement `plate_x < −0.15` and a ±0.15 ft dead zone reported as `middle` |
| Grain | `stand × h_side` |
| Population | P2 (tracked), `pitch_name == 'Slider'`; contact columns on P3 |
| CDEs | `pitch_name`, `plate_x`, `stand`, `type`, `launch_speed`, `events`, `description`, `estimated_woba_using_speedangle` |
| Rationale | A RHP slider is designed to finish away from a RHH. One that arrives arm-side did not finish — it backed up over the barrel. Raw slider whiff rate cannot separate execution from design; SFR can |
| Edge cases | Null `plate_x` excluded from denominator and counted in `excluded_null_loc` (0 here). Dead-zone pitches reported as `middle`, never folded into either side |
| Orientation proof | Statcast `plate_x` is catcher's-perspective, positive = first-base side. For a RHP, arm-side run ⇒ negative `plate_x`. **Verified empirically in the DQ scorecard**: sinker mean `pfx_x` < 0 and plate_x < 0; slider mean `pfx_x` > 0 and plate_x > 0. This assertion runs on every build |
| Status | **report-local → promotion candidate** |

**NEW-2 · Fastball Elevation Rate (FER)**

| Field | Spec |
|---|---|
| Plain language | What share of his four-seamers land in the upper third of *that hitter's* strike zone, and how does contact quality change by third? |
| Formula | `FER = count(FF in upper third) / count(FF with valid location)`, thirds computed per pitch against `sz_bot..sz_top` |
| Grain | `stand × v_third` |
| Population | P2, `pitch_name == '4-Seam Fastball'`; contact on P3 |
| CDEs | `pitch_name`, `plate_z`, `sz_top`, `sz_bot`, `stand`, `type`, `launch_speed`, `description`, `estimated_woba_using_speedangle` |
| Rationale | A 96.8 mph four-seamer with +15.7" IVB realises its value above the barrel plane. FER measures whether the pitch is used the way its shape dictates |
| Edge cases | Rows with null `plate_z`/`sz_top`/`sz_bot` excluded and counted. **Batter-height normalised** by construction — thirds use the per-pitch zone band, not a league-average box |
| Reporting note | Vertical thirds split contact into 2-21 BIP cells. The report and figure lead with **average exit velocity** (stable) and print the BIP denominator on every cell; xwOBAcon is corroboration only |
| Status | **report-local → promotion candidate** |

**NEW-3 · Role Conversion Delta (RCD)**

| Field | Spec |
|---|---|
| Plain language | For each locked process KPI, how much did the move to the bullpen change it — carrying both sample sizes so no one quotes the starting line as though it described today's pitcher |
| Formula | `delta = KPI(current era) − KPI(prior era)` per KPI, with `favourable_direction`, `improved`, both PA denominators, and `prior_below_threshold` |
| Grain | one row per KPI (10 KPIs) |
| Population | current = 2026 relief; prior = 2022-24 starting. **Never pooled** |
| CDEs | all CDEs feeding the locked KPI set |
| Rationale | The acquisition question is not "is he good" but "what did the role change do". RCD forces both denominators onto every conversion claim |
| Edge cases | **2025 excluded, not interpolated** — a true gap sits inside the comparison window and the KPI cannot see it. `prior_below_threshold` flags sub-100-BF prior tiers. `favourable_direction` prevents mis-signing an improvement (a falling BB% is good) |
| Status | **report-local → promotion candidate; the most reusable of the three** — any future converted acquisition inherits it directly |

**Mechanical partitions (not KPIs, no spec required):** `tracked()`, `zone_rate_strict()`, `add_movement_cols()`, `add_zone_thirds()`, `add_horizontal_side()`, `count_state()`. These re-express existing CDEs without introducing business meaning.

---

## 2.3 `eda-agent` — exploratory findings that shaped design

| Finding | Design consequence |
|---|---|
| Arsenal collapsed 6 → 4 pitches; cutter (27.6% of prior era) eliminated | Era-tier split is structural, not cosmetic — a pooled arsenal table would be meaningless |
| FF velocity +2.9 mph across eras | Confirms the conversion framing; RCD built to size it |
| All 5 home runs to RHH, all on the arm side of the plate | Motivated SFR. The horizontal-side cut was **not** in the original design — EDA put it there |
| Exit velocity rises monotonically as the FF descends, on both handedness sides | Motivated FER |
| Whiff rate and velocity flat across all 5 months | Monthly arc retained as a **negative** result — worth publishing because "no trend" is the answer to "what should we expect" |
| Whiff rate declines by batters-faced bucket while velocity holds | Motivated `batter_sequence`; distinguishes familiarity from fatigue, which is the difference between a leash recommendation and a conditioning one |

---

## 2.4 `join-validator` — join integrity

**No cross-domain joins exist in this data product.** Single source, single grain. The validator's normal checks are therefore scoped to internal consistency:

| Check | Result |
|---|---|
| Fan-out / row multiplication | ✅ n/a — no joins |
| Natural-key uniqueness after dedup | ✅ 0 duplicates on `(game_pk, at_bat_number, pitch_number)` |
| Grain drift across output tables | ✅ every table declares grain + population; P1/P2/P3 counts asserted in DQ |
| wOBA-constants merge (`game_year` → `Season`) | ✅ left join, 1:1 on season, no row multiplication; unmatched seasons would surface as null wOBA weights — none present |
| Era-tier partition is exhaustive and disjoint | ✅ 736 + 535 = 1,271 = total; no row in both tiers, none in neither (2025 contributes 0) |

**Verdict:** ✅ no join risk. The risk in this UC is *population selection*, not join logic — which is why the P1/P2/P3 lattice is the architect's headline deliverable.
