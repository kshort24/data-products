# The Directional Hitting Family
### What the guidebook now measures about where a ball was hit — and what the validation run found while proving it

**`uc-pos-017` · `dp_uc46` v1.0.0 · 2026-09-17 · verification 49/49 PASS · DQ 17 PASS / 1 WARN / 0 FAIL**
**Narrative reconciliation: **74 reconciliation checks** against the shipped receipts**
**Status: CONDITIONALLY CERTIFIED (C-1, C-2, C-3)**

---

## §1 · What was delivered

Seven certified functions, four governed KPIs, one closed defect.

| Object | What it is | Status |
|---|---|---|
| `hit_direction(level, df)` | The three-way spray classifier, **extracted** from inside `pull_air_rate` | GOVERNED |
| `derive_loc(level, df)` | `hc_x`/`hc_y` → field feet (PA-L1) | **RATIFIED — closes O-7** |
| `classifiable_bip(level, df)` | The governed directional population (DEN-1) | GOVERNED |
| `assert_spray_convention(level, df)` | Refuses to publish on an unverified coordinate convention | GOVERNED |
| `direction_rate(level, df)` | `pull_rate` · `straight_rate` · **`oppo_rate`** | GOVERNED |
| `bb_type_profile(level, df)` | `bb_type` shares + min/max/mean/std/p5/p95 per sensor | GOVERNED |
| `pull_air_rate(level, df)` | **Patched.** Runs for the first time. | GOVERNED, breaking |

**`oppo_rate` is a KPI of `direction_rate`, not a function of its own.** The wedge
boundary splits three ways, so `1 − oppo_rate` is not pull rate. Publishing the
three together makes that subtraction impossible to make by accident.

**`oppo_ld_rate` is materialised, not functionised.** `bb_type_profile` computes its
denominator at the level it is passed, so adding `hit_direction` to the level moves
the denominator from all BIP to oppo BIP — LD-1 satisfied by construction, with no
second implementation that could drift from the first:

```python
prof = bb_type_profile(['player_name', 'hit_direction'], bip)
prof.query("hit_direction == 'Oppo' and bb_type == 'line_drive'").share   # oppo_ld_rate
```

---

## §2 · The defect this build closed

`pull_air_rate` has been in the guidebook, described as *"an indicator of high
quality contact with an increased expectation of run production,"* and **has never
been able to execute.** It read `bip.loc_x` and `bip.loc_y`. The parquet schema has
`hc_x` and `hc_y` and no `loc_*` columns at all. Calling it raised.

That is not the interesting part. The interesting part is that **three delivered
use cases transcribed its body verbatim** — `dp_uc37`, `dp_uc40`, `dp_uc42` each
carry a hand-copied `hit_direction` — because the only authority for the ±4.7-slope
wedge boundary lived *inside* a broken function. Four copies of a definition, no
binding between them, and the canonical one did not run.

Extracting `hit_direction` as its own certified object is the smallest change in
this build and the one with the longest tail. Every directional function the
repository ever adds now inherits from one place.

---

## §3 · What the validation run found

The library was exercised against Phillies batting, 2024–2026 regular season:
12,360 balls in play, 12,351 classifiable.

### 3.1 The club's spray, three seasons

| Season | Classifiable BIP | Pull | Straightaway | Oppo |
|---|---|---|---|---|
| 2024 | 4,217 | 47.5% | 21.4% | 31.1% |
| 2025 | 4,232 | 47.3% | 23.5% | 29.3% |
| 2026 | 3,902 | **45.7%** | **24.5%** | 29.8% |

Pull rate has fallen 1.8 points across three seasons and straightaway has absorbed
all of it. Oppo is flat. Whatever is changing, it is not an opposite-field story —
it is balls that used to be pulled now going up the middle.

### 3.2 Pull is a ground-ball event. Oppo is an air event.

2026 batted-ball mix **within** each direction:

| Direction | Ground ball | Line drive | Fly ball | Popup |
|---|---|---|---|---|
| **Pull** | **60.1%** | 20.4% | 16.4% | 3.1% |
| Straightaway | 31.0% | 31.6% | 34.3% | 3.0% |
| **Oppo** | 28.6% | 25.2% | 32.5% | **13.7%** |

Three of every five pulled balls are on the ground. Fewer than three of every ten
opposite-field balls are.

This reframes `pull_air_rate`. The metric's premise is that pulling the ball in the
air indicates quality contact — and the data says the *air* qualifier is carrying
almost the entire signal, because pulled contact is overwhelmingly not in the air.
2026 pull rate is 45.7% and 2026 pull-air rate is 18.2%: **the qualifier removes
about 60% of the population it starts from.** Anyone reading "pull rate" and
"pull air rate" as near-relatives is reading two quite different things.

The popup column is the mirror image and the one nobody asks about: 13.7% of
opposite-field balls are popups against 3.1% of pulled balls. Going the other way
is, more than 4 times as often, going the other way badly.

### 3.3 Opposite-field contact is softer, and lands the same distance

2026 mean exit velocity by direction and type:

| Direction | Line drive | Fly ball | Ground ball |
|---|---|---|---|
| Pull | **96.0 mph** | 95.0 | 87.0 |
| Straightaway | 93.5 | 93.1 | 87.5 |
| Oppo | **91.1 mph** | 89.3 | 79.6 |

A pulled line drive leaves the bat **4.9 mph harder** than an opposite-field one.
But mean distance on those line drives is 251.9 ft pulled against 249.0 ft oppo —
essentially identical. The exit-velocity gap does not convert into a distance gap
on line drives; on fly balls it does, decisively (337.8 ft pulled vs 291.9 oppo).

**This is exactly the shape the profile arm was built to show.** A single "oppo
rate" number says a hitter went the other way. It cannot tell you that he went
there softer, or that the softness cost him 46 feet on fly balls and nothing on
line drives. That requires the `bb_type` cell to carry its own distribution — which
is what the DPO asked for, and it earns its place on the first run.

### 3.4 Opposite-field line-drive rate is remarkably stable

| Season | Oppo line drives | Oppo BIP | `oppo_ld_rate` | mean LA | mean EV |
|---|---|---|---|---|---|
| 2024 | 338 | 1,313 | **25.74%** | 17.1° | 92.4 mph |
| 2025 | 315 | 1,238 | **25.44%** | 17.3° | 91.5 mph |
| 2026 | 293 | 1,164 | **25.17%** | 16.8° | 91.1 mph |

Three tenths of a point of movement per season, across three seasons, on samples of
1,200+. Roughly one opposite-field ball in four is squared up, and that appears to
be close to a constant of the skill rather than a team characteristic.

That is a useful property for a KPI: a metric that barely moves at club level makes
**player-level** deviation legible. In 2026, Derek Hill put 40.5% of his balls in play the other way and Justin Crawford 39.0%,
against a club rate of 29.8%.

### 3.5 The handedness reversal

| Season | LHB oppo rate | RHB oppo rate |
|---|---|---|
| 2024 | 31.3% | 31.0% |
| 2025 | 28.5% | 29.9% |
| 2026 | **28.2%** | **31.8%** |

Even in 2024, 3.6 points apart in 2026 — the club's right-handed hitters now go the
other way meaningfully more often than its left-handed hitters. Both the classifier
and the boundary are handedness-symmetric by construction, so this is not a
measurement artifact. **It is not explained here.** Roster turnover, platoon
deployment, and opposing-pitcher mix are all live candidates and separating them is
a use case, not a footnote.

---

## §4 · What is deliberately not claimed

- **No causation.** §3.2 through §3.5 are descriptions of a population. Nothing here
  identifies why pull rate fell or why the handedness gap opened.
- **No player rankings below the floor.** Three of the twenty Phillies hitters with
  2026 batted balls fall under the 25-BIP floor and are suppressed, not ranked.
- **No comparison to league.** Every figure is Phillies-only. `oppo_rate` of 29.8%
  is a club rate with no benchmark behind it; whether that is high is unanswered.
- **No claim that pulling in the air is good.** §3.2 observes that the metric's
  qualifier removes most of its population. Whether the remainder is valuable is a
  `slg_bip`-style decomposition question, and `DC-1` from uc-pos-016 is the tool for
  it — not run here.

---

## §5 · Where this goes

The notecards (`dp_uc46_directional_notecards.html`) put the §3.3 finding in front
of a hitting coach for all 17 qualified hitters at once: directional share on top,
then the batted-ball mix and its distribution inside whichever direction you select.

The reusable governance output is `07_FUNCTION_CERTIFICATION_CHECKLIST.md` — ten
gates, domain-independent, with a mapping to the enterprise equivalents. It is the
direct answer to *"what makes a function acceptable in this repository"*, and the
two gates it names as most often missing are the two that would have caught the
O-7 defect years earlier.
