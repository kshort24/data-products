# 06 — Consumer Success

**Department:** `coa-dept-consumer-success` · **Lead:** `consumer-success-lead`
**Use Case:** `uc-pps-painter-return-001` · UC #29 · `dp_uc28`
**Layer 5 verdict:** ✅ artifacts staged — 2 consumer surfaces, 4 persona cards, query templates, data dictionary.

Agents run: `data-dictionary` · `analytics-enabler` · `consumer-onboarding-agent` · `query-builder` · `dashboard-specifier`.

---

## 6.1 `data-dictionary` — published field definitions

| Field | Type | Definition | Grain | Source CDE |
|---|---|---|---|---|
| `level` | string | Tier discriminator: `MLB` or `AAA`. **The governing dimension of this product** — no rate crosses it. | pitch | derived |
| `usage` | float | Share of pitches of this type within the group | level × pitch | `pitch_name` |
| `velo` | float | Mean release velocity, mph | any | `release_speed` |
| `velo_max` | float | Max release velocity observed, mph | any | `release_speed` |
| `spin` | float | Mean release spin rate, rpm | any | `release_spin_rate` |
| `ivb_in` | float | Induced vertical break, inches. Gravity-corrected. Higher = more "ride". | any | `pfx_z` × 12 |
| `hb_in` | float | Horizontal break, inches, **arm-side positive for a RHP**. Sign-flipped from raw Statcast. | any | `pfx_x` × −12 |
| `ext_ft` | float | Release extension toward the plate, feet | any | `release_extension` |
| `arm_angle` | float | Arm slot in degrees. **Statcast-derived, not directly measured** (fuzzy mapping, 03.2). | any | `arm_angle` |
| `velo_added_by_ext` | float | Perceived-velocity gain from extension, mph | level × pitch | `effective_speed` − `release_speed` |
| `whiff_rate` | float | Whiffs ÷ swings | any | `description` |
| `chase_rate` | float | Swings at out-of-zone pitches ÷ out-of-zone pitches | any | `zone` > 9, `description` |
| `in_zone_rate` | float | Pitches in the gridded zone ÷ all pitches | any | `zone` |
| `csw_rate` | float | (Called strikes + whiffs) ÷ pitches | any | `description` |
| `putaway_rate` | float | Strikeouts ÷ two-strike pitches | any | `strikes`, `events` |
| `first_pitch_strike_rate` | float | Non-balls on pitch 1 ÷ pitch-1 count | any | `pitch_number`, `type` |
| `hard_hit_rate` | float | Balls in play ≥95 mph EV ÷ balls in play. **Denominator is sparse** — 36% of pitches carry EV. | any | `launch_speed`, `type` |
| `loc_tier` | string | `heart` (in zone) / `shadow` (within a ball of the edge) / `chase` (competitive, out) / `waste` | pitch | `zone`, `plate_*`, `sz_*` |
| `rci_in` | float | **NEW** Release Consistency Index, inches. Within-start release dispersion, four-seam only. **Lower is tighter.** `NaN` if <15 four-seams. | level × start | `release_pos_x/z` |
| `futr` | float | **NEW** Fastball Upper-Third Rate. Share of four-seams at or above the upper third of the batter's own zone. **Not a quality score.** | any | `plate_z`, `sz_*` |
| `d_velo`, `d_spin`, `d_ivb`, `d_hb` | float | **NEW** Cross-Level Stuff Delta. AAA minus MLB, per pitch type. **Always read with `noise_guard`.** | pitch type | see 02.2 |
| `noise_guard` | string | `within measurement noise` if \|Δvelo\|<0.5 and \|Δride\|<1.0 and \|Δhoriz\|<1.0 | pitch type | derived |
| `coverage_ok` | bool | ≥15 pitches of that type in **both** tiers | pitch type | derived |
| `arm_spread_deg` | float | **PROVISIONAL** max − min mean arm angle across pitch types. Correlational tipping proxy. Not a ratified glossary term (03.1). | pitcher | `arm_angle` |
| `tto_lbl` | string | Times through the order: `1st time` / `2nd time` / `3rd+ time` | pitch | `at_bat_number`, `batter` |

---

## 6.2 `consumer-onboarding-agent` — persona cards

Four personas were named in the request. Each gets a different slice.

### 👤 Andrew Painter — *the pitcher*

> **Privacy ruling 03.4 R4 applies: this card is written in developmental language, not as a deficiency audit.** Painter is both the analysed entity and a consumer of this product.

**What this tells you:** your stuff is fine. Velocity, ride, and extension all sit mid-pack against big-league right-handers, and Triple-A didn't change them — nor did it need to. What changed is what you throw and when, and that change is the right one.

**Your three numbers:**
- **49.2%** — four-seam usage at Triple-A, up from 33.1% in the majors. Keep it there. Your worst seven-start stretch was your *lowest* fastball-usage stretch.
- **55%** — the elevation rate from your best Triple-A block. That's the target, not higher.
- **6.29 ft** — your extension on 7/26, down from 6.64 in April. This is the one to get back.

**What to do differently:** nothing dramatic. Trust the fastball, elevate to about 55%, and get down the mound instead of reaching for the extra tick. You've gained 0.6 mph and given back nearly two inches of extension to do it — in perceived terms that's close to a wash.

**What we're watching, and why you should know:** your arm slot varies more by pitch than almost anyone we can measure. That may be why a 96-with-ride fastball got a 10% whiff rate. It's a hypothesis, and we're testing it tonight rather than assuming it.

---

### 👤 J.T. Realmuto — *the catcher*

**What this tells you:** you're calling for a pitcher whose best swing-and-miss pitches got de-emphasised in the minors, and whose fastball plays better than it did in April.

**Your three numbers:**
- **.395** — splitter whiff rate against lefties, on 76 major-league swings. His best pitch. At Triple-A he threw it half as often.
- **.150** — his Triple-A whiff rate against lefties, without it.
- **10.2°** — the arm-angle gap between his four-seam and his sweeper. The widest in his arsenal.

**Your three calls:**
1. Splitter to lefties with two strikes, **buried** — down and arm-side. He threw it in the zone only 18.5% of the time at Triple-A and still got a .409 chase rate. It works when it's not competitive.
2. Never four-seam into sweeper back-to-back to the same hitter early. Break it with the sinker or slider, which sit between them in slot.
3. First inning: watch where the four-seam is coming out. Around −20 inches instead of −25 is the 6/17 and 6/28 signature — his two shakiest outings.

**Which view to open:** the dashboard's **Platoon & sequencing** tab, with the handedness toggle. Every pitch shows usage and whiff for both levels side by side.

---

### 👤 Pitching department — *the coaches*

**What this tells you:** the diagnosis isn't "he needs a better pitch." It's "his best pitch doesn't play like its shape says it should," and there's a measurable candidate for why.

**Your three numbers:**
- **13.8° vs 4.25°** — his arm-slot spread against the pool median. 96th percentile.
- **26th / 23rd percentile** — his four-seam whiff overall and up in the zone, on 55th-percentile velocity and 52nd-percentile ride.
- **7.03 mph** — his splitter's separation from the fastball at Triple-A, down from 9.13.

**Your three actions:**
1. Slot uniformity is the highest-leverage cue you have. Everything else in his profile says the fastball should work.
2. Instrument tonight — first-pitch swing rates and whiff-by-pitch after same-slot vs different-slot sequences. One start won't settle it; the data costs nothing to collect.
3. Decide on the splitter. Harder and flatter-released means it's drifted out of the fastball tunnel. Either pull the velo back toward 87–88 and restore the slot match, or stop asking it to be a chase pitch.

**Which view to open:** the dashboard's **Delivery & release** tab. Arm angle by pitch type, release drift by start, and the spread-vs-pool table.

---

### 👤 Manager — *in-game decisions*

**What this tells you:** how long to run him, and what to watch for that means "now."

**Your three numbers:**
- **85–90 pitches.** Triple-A counts were 80, 69, 70, 87, 90. Five or six innings, not more.
- **25% chase.** Under that through two innings is the warning. A .265 chase rate over seven starts is exactly what got him optioned.
- **.315 → .359 → .429** — hard-hit rate by times through the order in the majors. The same climb shows at Triple-A. The bats get on him progressively.

**Your leash markers, in order:**
1. Four-seam release drifting toward −20 inches — the mechanical tell.
2. Chase under 25% through two — the deception tell.
3. Hard contact climbing — the one weakness that never went away at either level.

**Have someone warm before the third time through.** The outcome numbers don't scream it; the contact quality does.

**Which view to open:** the dashboard's **Overview** tab. Times-through-order chart, plus the six headline KPI cards.

---

## 6.3 `query-builder` — validated templates

All templates assume the receipts in `out/`. Load once:

```python
import pandas as pd, os
OUT = "out"
rd = lambda n: pd.read_csv(os.path.join(OUT, f"dp_uc28_{n}.csv"))
```

**Q1 — "What does he throw, and how often, at each level?"**
```python
a = rd("arsenal_by_level")
a.pivot(index="pitch_name", columns="level", values="usage")
```

**Q2 — "Which pitch actually changed at Triple-A?"**
```python
s = rd("stuff_delta")
s.loc[s.coverage_ok & (s.noise_guard == "outside noise band"),
      ["pitch_name", "d_velo", "d_spin", "d_ivb", "d_hb", "d_usage_pp"]]
```

**Q3 — "How does his fastball compare to other big-league right-handers?"**
```python
rd("ff_benchmark_painter")[["metric", "painter_mlb", "pool_median", "painter_mlb_pctile"]]
```

**Q4 — "Is elevating the fastball working?"**
```python
f = rd("fastball_whiff_by_location")
f[f.cut == "elevation band"][["level", "loc_tier", "swings", "whiff_rate"]]
```

**Q5 — "What should we throw this lefty with two strikes?"**
```python
u = rd("usage_by_stand")
u[(u.stand == "L") & (u.swings >= 10)].sort_values("whiff_rate", ascending=False)[
    ["level", "pitch_name", "usage", "swings", "whiff_rate"]]
```

**Q6 — "Where is his release point tonight vs the baseline?"** *(the in-game check)*
```python
r = rd("release_by_start")
baseline = r[~r.game_date.isin(["2026-06-17", "2026-06-28"])].mean_x_ft_in
print(f"baseline band: {baseline.min():.1f} to {baseline.max():.1f} in")
print("ALERT if tonight's 4-seam mean release_pos_x*12 is above -22 in")
```

**Q7 — "When do we get someone up?"**
```python
t = rd("times_through_order")
t[t.level == "MLB"][["tto_lbl", "plate_apps", "hard_hit_rate", "whiff_rate"]]
```

> ⚠️ **Guard rail on every template:** do not concatenate MLB and AAA rows and recompute a rate. The receipts are pre-split by `level` for exactly this reason (03.1).

---

## 6.4 `dashboard-specifier` — specification and build

**Delivered:** `dp_uc28_painter_vs_orioles_dashboard.html` — self-contained, opens in any browser, no server.

| Element | Spec |
|---|---|
| **Data source** | Reads `out/dp_uc28_*.csv` at build time, inlines as JSON. **No recomputation in the browser** — cannot drift from the PDF. |
| **Tabs** | Overview · Arsenal & stuff · The fastball problem · Delivery & release · Platoon & sequencing · Start log · Governance |
| **Filters** | level toggle (both / MLB / AAA); metric selector on the arsenal chart; handedness toggle on the platoon tab |
| **Default view** | Overview — six KPI cards, level comparison, both arcs, times-through-order |
| **Drill-down** | every chart tooltip carries the sample size (n, swings) alongside the rate |
| **Persistent warning** | the data-window box is fixed above the tabs, not tucked in a tab — it cannot be navigated away from |
| **Governance tab** | full DQ scorecard with PASS/WARN/**FAIL** pills and the freshness manifest, shipped *to the consumer*, not just to the DPO |
| **Brand** | Phillies red `#E81828`, navy `#002D72` |
| **Charts** | Chart.js 4.4.1 from cdnjs (approved CDN) |

**Two specification decisions worth recording:**

1. **The governance tab is consumer-facing.** Most dashboards hide their DQ scorecard. This one ships it, including the FAIL, because a coach reading "no Orioles data" is better served than a coach who assumes the opponent analysis simply wasn't interesting.
2. **Sample size travels with every rate.** The platoon tooltip reads `10.6% (n=27, whiff 35.7% on 14 sw)` rather than `10.6%`. On a 101-PA tier, a rate without its denominator is a hazard.

---

## 6.5 `analytics-enabler` — FAQ

**Q: Why can't I just compare his AAA numbers to his MLB numbers directly?**
Because Triple-A hitters aren't big-league hitters. Anything that depends on hitter quality — whiff, chase, hard-hit, wOBA — is interpretable within a level and directionally across levels, never as an equivalence. His .212 Triple-A four-seam whiff rate is exactly the *median MLB* four-seam rate. That's real progress from .106 and it isn't a weapon yet. Stuff measurements (velocity, spin, movement, release) *do* compare directly.

**Q: The report says his stuff didn't change. Then what did Triple-A accomplish?**
A re-sequencing. He went from 33% four-seams to 49% and cut his slider by 13 points. That's an attack-plan rebuild, and it addresses the actual failure — over his last seven big-league starts he threw his fastball 27.7% of the time and his strikeout rate fell to .150.

**Q: Is the tipping thing established?**
No, and the report says so twice. It's the best available explanation for average shape plus average location plus bottom-quartile bat-missing, and his slot spread really is 96th percentile. It's a hypothesis with support, being tested tonight.

**Q: Why is there no scouting on the Orioles?**
There is no Orioles data in this repo, and Painter has never faced them. Fabricating a lineup plan was rejected at intake. The gap is recorded as a FAIL in the DQ scorecard and stated in the report's warning box.

**Q: Why does the report avoid xwOBA?**
`estimated_woba_using_speedangle` is populated on 26% of pitches and was deprecated at pitch level by the UC-PPS-021 (Nola) data-quality fix. That ruling is inherited here.

**Q: Can I share this?**
Internal only. `privacy-watchdog` blocked external publish and set a need-to-know distribution — the four named personas plus the human DPO. This package contains a tipping hypothesis and per-pitch release signatures on our own pitcher; in an opponent's hands it's an attack plan against him.
