# 06 — Consumer Success

**Department:** Consumer Success · **Agents:** `data-dictionary`, `analytics-enabler`, `consumer-onboarding-agent`, `query-builder`, `semantic-modeler`, `dashboard-specifier`

---

## 6.1 `data-dictionary` — published column reference

### `dp_uc29_role_conversion_delta.csv` — **NEW KPI**

| Column | Type | Meaning | Range | Nulls |
|---|---|---|---|---|
| `kpi` | str | Locked KPI name | 10 rows | — |
| `prior_2022_24_start` | float | Value in the starting era | — | — |
| `current_2026_relief` | float | Value in the relief era | — | — |
| `delta` | float | current − prior (**signed**) | — | — |
| `favourable_direction` | str | `+` if higher is better, `-` if lower is better | — | — |
| `improved` | bool | Direction-aware verdict — **read this, not the sign of `delta`** | — | — |
| `prior_PA` / `current_PA` | int | Both denominators, always carried | 138 / 193 | — |
| `prior_below_threshold` | bool | True if prior era < 100 BF | False here | — |

### `dp_uc29_slider_finish.csv` — **NEW KPI**

| Column | Type | Meaning | Nulls |
|---|---|---|---|
| `stand` | str | Batter handedness | — |
| `h_side` | str | `glove side` / `middle` / `arm side` — where the pitch **arrived** | — |
| `pitches` | int | Sliders thrown to that side | — |
| `share_of_sliders` | float | The SFR itself — share within handedness | — |
| `swings`, `whiffs`, `whiff_rate` | int/float | Swing outcomes | `whiff_rate` null if 0 swings |
| `bip`, `avg_ev`, `xwobacon` | int/float | Contact quality, **BIP-only** | null if 0 BIP |
| `hr` | int | Home runs allowed | — |
| `excluded_null_loc` | int | Sliders dropped for null location | 0 here |

### `dp_uc29_fastball_elevation.csv` — **NEW KPI**

| Column | Type | Meaning |
|---|---|---|
| `stand`, `v_third` | str | Handedness; `upper`/`middle`/`lower` third of **that batter's** zone |
| `pitches`, `elevation_rate` | int/float | Count; share within handedness |
| `swings`, `whiffs`, `whiff_rate` | int/float | Swing outcomes |
| `bip`, `avg_ev`, `xwobacon` | int/float | Contact quality, BIP-only — **cells run 2-21 BIP; read `avg_ev`, not `xwobacon`** |

### Direction semantics

**Higher is better:** `whiff_rate`, `chase_rate`, `putaway_rate`, `first_pitch_strike_rate`, `csw_rate`, `krate`, `elevation_rate`, glove-side `share_of_sliders`.
**Lower is better:** `bbrate`, `hard_hit_rate`, `avg_ev`, `xwobacon`, `woba`, `hr_rate`, arm-side `share_of_sliders`.

### Sample discipline — the rule for reading this data product

Every rate cell carries its denominator. **193 PA (2026 tier) is the only sample in this product that clears the 100-BF publishing convention on its own.** Platoon splits (110 / 83 PA) and every pitch × hand cell (3-40 BIP) are directional. Where a cell is thin, prefer **exit velocity and raw counts** over rate metrics.

---

## 6.2 `semantic-modeler` — KPI semantic layer

**Aggregation constraints — the rules that prevent metric drift:**

| Constraint | Rule |
|---|---|
| **Era tiers never blend** | `2026 SF (relief)` and `2022-24 CHC (start)` may not be pooled into a single rate. Any query returning one number across both eras is invalid |
| **Population must match metric class** | Usage/zone/location metrics → tracked pop (728). PA outcomes → full pop (736). Contact metrics → BIP (118). Mixing produces the O2/O3 defect class |
| **Rates are not re-averageable** | `whiff_rate` across cells must be recomputed from `whiffs`/`swings`, never averaged. Same for every ratio in this product |
| **xwOBAcon is BIP-only** | The pitch-level `get_stats.xwoba` column is **quarantined**. Any consumer computing xwOBA must filter `type=='X'` |
| **Exit velocity is BIP-only** | `launch_speed` is populated on fouls. Every mean must filter `type=='X'` |
| **`improved` is direction-aware** | Never infer improvement from the sign of `delta` alone |

**Valid dimensions:** `era_tier`, `game_year`, `month`, `stand`, `pitch_name`, `count_state`, `h_side`, `v_third`, `seq_group`, `entry_inning`, `score_state`.
**Invalid dimension:** opponent — descoped, no opponent data exists in this product.

**Versioning:** `dp_uc29` v1.0. New product, no consumers, no breaking-change surface.

---

## 6.3 `analytics-enabler` — how to use this data product

**Start here:** `dp_uc29_kilian_acquisition_read_report.pdf` (9 pages). Bottom Line answers the acquisition question in five numbered findings; each persona has its own section.

**Common query patterns:**

```python
import pandas as pd
OUT = "data-products/uc-pps-024-kilian-acquisition-001/out/"

# "Is the conversion real?" — direction-aware, both denominators
rcd = pd.read_csv(OUT + "dp_uc29_role_conversion_delta.csv")
rcd[["kpi", "prior_2022_24_start", "current_2026_relief", "delta", "improved"]]

# "Should he face this hitter?" — always with denominators attached
pbh = pd.read_csv(OUT + "dp_uc29_pitch_by_hand.csv")
pbh[pbh.stand == "L"][["pitch_name", "pitches", "usage", "whiff_rate", "bips", "avg_ev", "hr"]]

# "Where does the slider play?" — the headline coaching finding
pd.read_csv(OUT + "dp_uc29_slider_finish.csv").query("stand == 'R'")

# "How long can I leave him in?"
pd.read_csv(OUT + "dp_uc29_batter_sequence.csv")[["seq_group","plate_apps","whiff_rate","avg_ev","ff_velo"]]
```

**Interpreting the headline KPIs:**

- **Slider Finish Rate.** 52.5% glove-side vs RHH. Target **70%+**, arm-side below 15%. Arm-side sliders carry 3 of his 5 career-2026 home runs. Rising SFR is the leading indicator that the primary coaching intervention is working.
- **Fastball Elevation Rate.** 52.9% upper-third vs LHH, 46.4% vs RHH. The lower third is where contact hardens (94-98 mph). Against RHH he goes lower-third 33.3% of the time — the biggest single location leak.
- **Role Conversion Delta.** All 10 KPIs improved. Read `improved`, not the sign of `delta`. Note that xwOBAcon improved by only .024 — **the conversion bought contact *avoidance*, not contact *management*.**

**FAQ**

> **Why no opponent section?** No role has been assigned and he has never pitched for the organization. Descoped deliberately (01 §V1) with a follow-on trigger.
> **Why is 2025 blank?** No MLB service; no minor-league cache in this repo. A true gap, never interpolated — and it sits *inside* the conversion window, which is this product's largest interpretive limitation.
> **Why does he strike out more righties but give up all the damage to them?** That is the central finding. Results and process agree in the same direction, so the split is real — but it rests on 83 PA. Treat as a strong prior, re-test at 150 PA.
> **Why is zone rate 48.1% here and 48.6% elsewhere?** Untracked `automatic_ball` rows inflate the locked calculation. This product publishes the strict variant. See O2.
> **Can I average `avg_ev` across cells?** No. Recompute from balls in play.

---

## 6.4 `consumer-onboarding-agent` — persona guides

### Pitching coach / pitching department
**Your section:** "For the pitching department — the development plan."
**Your KPIs:** Slider Finish Rate (primary), Fastball Elevation Rate (secondary).
**Your three actions:** fix the slider finish; re-weight the arsenal vs RHH (knuckle curve up from 15.1%, it whiffs at 66.7%); retire the sinker vs LHH.
**What not to do:** don't chase the velocity — it is stable across five months and holds in second innings. There is no conditioning problem to solve.

### Catchers + Kilian
**Your section:** "For the battery — the pitch-selection card."
**Your one rule:** *fastballs up, breaking balls glove-side, never let the slider drift back arm-side to a righty.*
**Vs LHH:** four-seam up, knuckle curve to finish, shelve the sinker.
**Vs RHH:** open with the sinker, **knuckle curve is the out pitch — not the slider**, slider only glove-side and below the belt.
**Reading the numbers:** where a cell shows fewer than ~15 balls in play, it is a lean, not a law. The card marks these.

### Manager (Don Mattingly)
**Your section:** "For the manager — how to use him."
**Your KPIs:** batters-faced sequence (the leash), platoon split, entry score state.
**Four takeaways:** one inning / four batters then get him; point him at left-handed stretches; not a one-run ninth *yet*; available on short rest and can go two.
**The counterintuitive one:** he strikes out righties far more and gives up **all** the damage to them. The strikeout column will fight this recommendation. Trust the damage column — but re-check at 150 PA.

### Analyst / front office
**Your section:** the full report plus `05_quality_certification.md`.
**Start with:** `role_conversion_delta.csv` and the caveats section.
**Know before you cite:** the 2025 gap sits inside the conversion window; the prior era is 8 starts; xwOBAcon is BIP-only; usage rates use 728 tracked pitches.

---

## 6.5 `query-builder` — validated templates

```python
# Q1. "What did the bullpen move actually change?"
rcd = pd.read_csv(OUT + "dp_uc29_role_conversion_delta.csv")
assert rcd.improved.all()          # all 10 KPIs improved
rcd.loc[rcd.kpi == "xwOBAcon"]     # ...but contact quality only marginally

# Q2. "Righty or lefty?" — recompute rates, never average them
p = pd.read_csv(OUT + "dp_uc29_platoon.csv")
p[["stand","plate_apps","krate","whiff_rate","hard_hit_rate","avg_ev","xwobacon","hrs"]]

# Q3. "How bad is the backed-up slider?"
s = pd.read_csv(OUT + "dp_uc29_slider_finish.csv").query("stand=='R'")
s["hr_per_pitch"] = s.hr / s.pitches      # arm side: 3/15; glove side: 0/32

# Q4. "When do I go get him?"
pd.read_csv(OUT + "dp_uc29_batter_sequence.csv")   # whiff falls, EV climbs, velo flat

# Q5. "Was he a closer?"
d = pd.read_csv(OUT + "dp_uc29_deployment.csv")
d[d.entry_inning == 9].groupby("score_state").outings.sum()   # 13 of 20 up 2+; only 2 up 1
```

---

## 6.6 `dashboard-specifier` — spec (not built)

Recommended for a future build if this pattern is repeated across the remaining deadline acquisitions:

| Panel | Chart | Filter | Drill-down |
|---|---|---|---|
| Conversion scorecard | Diverging bar, direction-aware | — | → season log |
| Arsenal map | Scatter IVB × HB, size = usage | era tier | → pitch × hand |
| Location damage | Zone heat map, EV-coloured | pitch, hand | → damage log |
| Deployment | Stacked bar, inning × score state | — | → outing log |
| Leash | Dual-axis whiff / EV by BF bucket | hand | → PA detail |

**Mandatory:** every cell displays its denominator; any cell below 15 BIP renders with a directional marker. **Not built this session** — a static PDF meets the stated need, and a dashboard should be built once for the whole acquisition cohort rather than per player.
