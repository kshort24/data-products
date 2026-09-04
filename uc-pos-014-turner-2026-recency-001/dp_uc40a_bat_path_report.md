# Trea Turner — How He Is Meeting the Ball

### `uc-pos-014` **v1.1.0** addendum · `dp_uc40a` · bat-path deep dive · Phillies Offense · as of **2026-09-02**

> **What this adds.** v1.0.0 found that the popup rate was the one signal clearly beyond noise
> (15.2% of balls in play since 1 August vs a 5.0% Phillies norm, z = 4.12) but could only describe the
> *outcome*. Statcast's bat-path columns describe the *swing*. This addendum defines those columns for
> the data plane — none had a governed definition before this build — and uses them to answer **how**
> he is meeting the ball, at the `pitch_group` grain.
>
> **Coverage boundary.** `attack_angle`, `attack_direction`, `swing_path_tilt` and the two intercept
> components ship from **2025 only**; `bat_speed` and `swing_length` from 2024. There is **no bat path
> before 2025**, so every comparison here is 2025 vs 2026 — two seasons, not a career arc. Coverage on
> Turner's swings is 95.1% (2025) and 96.1% (2026): stable, so the year-over-year comparison is legitimate.
> **12/12 convention assertions pass** and the build refuses to publish if any fails; every number
> below was recomputed on an independent code path — **180/180 PASS**.

---

## §1 · The verdicts

| # | Question | Verdict | The number |
|---|---|---|---|
| **1** | Do the bat-path columns explain the popups? | **Yes — two changes, both beyond noise** | **Swing plane flattened 27.9° → 25.5°** (z = −12.4) and **contact moved 1.35″ further from his body** (z = +4.5). Everything else is noise once peer-netted |
| **2** | Is it bat speed? | **No — confirmed a second time** | 69.5 → **70.2 mph**, peer-netted **+0.49**. v1.0.0 said bat speed was a red herring; the path data says the same thing from a different direction |
| **3** | Is it attack angle? | **No** | 7.55° → 8.28°, but peer-netted only **+0.21°**. His attack angle lands in the ideal 5–20° window on **61.7% of swings — the 82nd percentile** of Phillies hitters. The angle at contact is fine |
| **4** | Is the popup problem pitch-group specific? | **Almost entirely breaking balls** | Popup rate on breaking balls **3.9% → 12.1%**. Fastball **4.7% → 4.2%**, offspeed **4.2% → 4.7%** — both flat. Four-season view: breaking .040 / .072 / .039 / **.121** |
| **5** | Is that just the league? | **No — he is the outlier, but the tide rose too** | The Phillies peer median for breaking-ball popups also doubled (3.8% → 7.5%). Turner went from **rank 6 of 12 (exactly the median)** to **rank 1 of 10, +4.6 points clear** |
| **6** | How flat is flat? | **Flattest bat on the roster** | 25.5° is the **minimum of all 11 Phillies with 200+ tracked swings — 0th percentile**. MLB average is ~32° |
| **7** | Does the popup swing look different from his other contact? | **Yes, and consistently** | Popups: attack angle **10.7° vs 6.9°**, plane **23.4° vs 25.2°**, contact **2.3″ closer to the body** and **4.7″ further out front**, on pitches **0.31 ft higher** — at the *same* bat speed |
| **8** | Has the path moved with the slump? | **The path was already flat; the popups arrived later** | Tilt is 25.6 / 25.3 / 25.9 across the three 2026 windows — flat all year. Breaking-ball popup rate: **8.4% → 4.5% → 22.7%**. The mechanism was in place before the outcome showed up |

**One sentence:** Turner has flattened his swing plane more than any teammate and moved his contact point
away from his body, and against breaking balls — which arrive on a steeper descending plane than
fastballs — that combination turns a fractionally mistimed swing into a pop-up instead of a mishit.
**The bat is fine. The plane is flat and the contact point has drifted.**

---

## §2 · What the columns are (they had no definition here before this build)

Six physical columns, none of which had a governed definition in the data plane. `03a` carries the full
semantic and technical spec, lineage, and the assertion battery. The short version:

| Business term | Physical column | Units | What it measures |
|---|---|---|---|
| **Attack angle** | `attack_angle` | ° | **Vertical** direction the sweet spot is travelling **at contact**. + = upward. MLB avg ≈ 10°; "ideal" band 5–20° |
| **Attack direction** | `attack_direction` | ° | **Horizontal** direction the sweet spot is travelling **at contact**. 0° = centre field |
| **Swing path tilt** | `swing_path_tilt` | ° | Tilt of the swing **plane on the way to contact**, versus the ground. 0° = flat, 90° = golf swing. MLB avg ≈ 32° |
| **Contact point — side** | `intercept_ball_minus_batter_pos_x_inches` | in | **Lateral** distance from the batter's centre of mass to the contact point |
| **Contact point — depth** | `intercept_ball_minus_batter_pos_y_inches` | in | Distance the contact point is **out in front of** the batter's centre of mass |
| *(not a bat-path column)* | `hyper_speed` | mph | **O-17:** proven to be exactly `max(launch_speed, 88)`. Carries no information beyond exit velocity |

**Two of those rows are findings, not documentation.** The axis assignment and the sign convention were
**proven against the data**, not read off the glossary — and one of them contradicts it:

- **O-15 · `attack_direction` is PULL-NEGATIVE in this data plane.** The published MLB glossary states
  "Pull = positive values." In `phils_*.parquet` the sign is inverted, and four independent anchors agree:
  correlation with pull-side spray on hard-hit air balls is **−0.79**; correlation with contact depth is
  **−0.89**; 96+ mph fastballs (met deep, fought off) sit at **+12.9** while sub-80 mph breaking balls (met
  out front, pulled) sit at **−16.3**; and the sign behaves identically for left- and right-handed hitters,
  so it is a stand-normalised convention, not a field frame. **Anyone applying the glossary convention to
  this column inverts every pull/oppo conclusion they draw from it.** Both the raw column and a corrected
  `pull_direction` ship in every receipt.
- **The two intercept components are side and depth — there is no height component.** Proven: the side
  axis correlates **−0.95 / −0.89** (RHH / LHH) with how far inside the pitch is, and the depth axis
  correlates **−0.56** with pitch velocity, which is the exogenous timing anchor — a slower pitch is met
  further out front, monotonically from 20.4″ on 96+ mph to 41.1″ under 80 mph.

---

## §3 · What actually changed in the swing

![peer-netted deltas](dp_uc40a_fig2.png)

Two seasons of the same instrument, and a **peer control** — because the swing-tilt column moved
team-wide (O-16) and a raw year-over-year delta on an instrumented column cannot tell a swing change from
a calibration change. Cohort: the 8 Phillies hitters with 200+ tracked swings in **both** 2025 and 2026.

| Measure | 2025 | 2026 | Raw Δ | Peer median Δ | **Peer-netted Δ** | Rank in cohort | ST-1 band |
|---|---|---|---|---|---|---|---|
| **Swing path tilt (°)** | 27.86 | **25.51** | −2.35 | −1.15 | **−1.20** | **1 of 8 (largest drop)** | **z = −12.4, clearly beyond noise** |
| **Contact point, side (in)** | 37.83 | **39.18** | +1.35 | +0.18 | **+1.17** | **8 of 8 (largest increase)** | **z = +4.5, clearly beyond noise** |
| Attack angle (°) | 7.55 | 8.28 | +0.73 | +0.52 | +0.21 | 7 of 8 | z = 2.03, suggestive |
| Attack direction (°) | −1.34 | −2.77 | −1.43 | −1.10 | −0.33 | 4 of 8 | z = −1.55, suggestive |
| Bat speed (mph) | 69.52 | 70.18 | +0.66 | +0.17 | +0.49 | 7 of 8 | z = 2.29, suggestive |
| Contact point, depth (in) | 28.46 | 29.17 | +0.71 | +0.71 | **+0.00** | 5 of 8 | z = 1.32, within noise |
| Swing length (ft) | 7.48 | 7.53 | +0.05 | +0.01 | +0.04 | 7 of 8 | z = 1.57, suggestive |

**Only two things moved.** The plane got flatter and the contact point moved away from the body. The
peer control is doing real work here: the raw tilt delta is −2.35°, but roughly half of that is a
team-wide shift that no single hitter caused. **The half that is his is still the largest in the cohort.**

**Where that leaves him against the roster.** Among the 11 Phillies with 200+ tracked swings in 2026:

| Measure | Turner 2026 | Pool median | Pool range | Percentile |
|---|---|---|---|---|
| **Swing path tilt** | **25.51°** | 30.83° | 25.51 – 37.29 | **0th — he *is* the minimum** |
| Contact point, side | 39.18″ | 37.58″ | 33.16 – 41.83 | 73rd |
| Ideal-attack-angle rate (5–20°) | 61.7% | 53.0% | 36.9 – 65.0 | 82nd |
| Attack angle | 8.28° | 9.07° | 2.56 – 14.71 | 27th |
| Bat speed | 70.18 mph | 70.18 | 61.47 – 74.58 | 45th |

He owns the flattest swing plane on the roster by a margin, while his angle *at contact* is one of the
best-placed on the team. Those two facts together are the whole finding: **the barrel arrives at a good
angle, but on a plane that gives it very little margin.**

---

## §4 · Why breaking balls, specifically

![popup rate by pitch group](dp_uc40a_fig1.png)

Popup rate by pitch group — using the `pitch_group` mapping from the data plane, unchanged:

| Pitch group | 2023 | 2024 | 2025 | **2026** | 2026 BIP |
|---|---|---|---|---|---|
| **Breaking** | 4.0% | 7.2% | 3.9% | **12.1%** | 149 |
| Fastball | 6.5% | 4.1% | 4.7% | **4.2%** | 236 |
| Offspeed | 4.8% | 5.1% | 4.2% | **4.7%** | 43 |

**The entire increase is breaking balls.** Fastball and offspeed popup rates are inside their own
four-year range. Breaking-ball popups roughly tripled against his 2025 and 2023 baselines.

**And it is not just the league.** Among Phillies hitters with 40+ breaking balls in play:

| | 2025 | 2026 |
|---|---|---|
| Peer median breaking-ball popup rate | 3.8% (12 qualifiers) | 7.5% (10 qualifiers) |
| **Turner** | **3.9% — rank 6 of 12, exactly the median** | **12.1% — rank 1 of 10** |
| Turner minus the peer median | **+0.1 pts** | **+4.6 pts** |

The peer median itself doubled, which is a real caveat and is why the row above exists. But Turner moved
from the middle of his own clubhouse to the top of it, and the gap he opened is larger than the tide.

**The mechanics, on breaking balls only** (2025 → 2026, tracked swings 409 → 390):

| Measure | 2025 | 2026 | Δ | ST-1 band |
|---|---|---|---|---|
| **Swing path tilt** | 28.09° | **25.59°** | −2.50 | **z = −8.2, clearly beyond noise** |
| **Contact point, side** | 39.31″ | **41.01″** | +1.70 | **z = +3.3, clearly beyond noise** |
| Bat speed | 68.63 | 69.68 | +1.05 | z = 2.00, suggestive |
| Attack angle | 10.68° | 11.30° | +0.62 | z = 1.07, within noise |
| Attack direction | −12.33° | −13.89° | −1.56 | z = −1.08, within noise |
| Contact point, depth | 35.36″ | 36.06″ | +0.69 | z = 0.79, within noise |

![swing path by pitch group](dp_uc40a_fig4.png)

The same two changes, slightly larger on breaking balls than overall. **Against a breaking ball he is now
reaching 41 inches from his body on a 25.6° plane** — the flattest, longest-reaching combination he has
put on tape in the two years the instrument has existed.

Note the pitch-group contrast that makes it mechanical rather than mental: on **fastballs** he meets the
ball at 38.1″ and 23.2″ out front with a **5.6°** attack angle; on **breaking balls**, 41.0″ and 36.1″ out
front with an **11.3°** attack angle. Breaking balls are met further away and further out front, with the
barrel climbing more steeply — the exact geometry in which a flat plane runs out of margin.

---

## §5 · The popup swing itself

![the popup swing](dp_uc40a_fig3.png)

Popups versus every other tracked ball in play, 2026 (26 vs 374):

| Measure | Other BIP | **Popups** | Δ |
|---|---|---|---|
| Attack angle | 6.89° | **10.73°** | **+3.8°** |
| Swing path tilt | 25.23° | **23.42°** | −1.8° |
| Contact point, side | 39.52″ | **37.23″** | **−2.3″ (closer to the body)** |
| Contact point, depth | 27.01″ | **31.71″** | **+4.7″ (further out front)** |
| Pitch height at the plate | 2.34 ft | **2.65 ft** | +0.31 ft |
| **Bat speed** | 71.53 | **71.20** | **−0.33 — no difference** |
| Launch angle / exit velo | 6.7° / 88.6 | 66.4° / 77.6 | — |

**The popup swing is not a slow swing.** It is a swing that arrives on a flatter plane with a steeper
barrel angle, on a higher pitch, meeting the ball further out front and tucked closer to the body. That
is the signature of getting the barrel *under* the ball with the hands ahead of it, not of a defensive
or checked swing.

**Honesty note on the within-2026 breaking-ball contrast.** Restricting to breaking balls, popups (15
tracked BIP) versus non-popups (122) shows the same directional pattern but only **contact side clears
even the suggestive bar** (−3.0″, z = −1.93); everything else is inside noise at that sample. **The
strong evidence in this addendum is the season-level profile change, not the within-window contrast.**

**A build note that changed a number.** An earlier pass over an ungoverned population had breaking-ball
popups arriving at 63.6 mph of bat speed — a 7-mph collapse, and a compelling story. Applying the O-18
population rule (exclude bunts; flag swings under 25 mph as degenerate) removed a handful of checked
swings and the gap vanished to −0.5 mph. **The population rule killed the story.** It is recorded here
because the ungoverned version was the more quotable one.

---

## §6 · What the hitting department can test

Same discipline as v1.0.0 §8: **no causation is identified anywhere in this data plane.** These are
observables mapped to remit, ranked by how much of the popup gap they could plausibly close.

| # | Observable | Persona | Testable hypothesis | Read-out that would confirm it |
|---|---|---|---|---|
| **1** | Swing plane **25.5° — the flattest on the roster**, MLB average ~32°, and the largest peer-netted drop in the cohort | **Hitting coach** | A plane-steepening cue (rear shoulder, hand path under the ball) is the single most specific intervention this data supports. He does **not** need a bigger attack angle — his ideal-attack-angle rate is already 82nd percentile — he needs the barrel on the ball's plane for longer | `swing_path_tilt` moving back toward 27–28° **without** attack angle rising past ~12°, and breaking-ball popup rate falling toward 5% |
| **2** | Contact point **1.2″ further from the body** (peer-netted), **1.7″ on breaking balls**; popups are met **2.3″ closer in and 4.7″ further out front** | **Hitting coach / player development** | Contact-depth work: let breaking balls travel, keep the hands closer. The popup geometry is hands-ahead-of-barrel, which is a depth problem before it is a plane problem | `intercept_side_in` on breaking balls back under 40″; popup contact depth converging on his non-popup depth |
| **3** | Breaking-ball popup rate 3.9% → 12.1%, **+4.6 pts clear of a peer median that itself doubled**; breaking usage against him climbed 34.6% → 40.3% (v1.0.0 §7) | **Advance scouting** | The league is feeding the weakness. Machine and live work weighted to breaking balls at the top of the zone — popup pitch height averages 2.65 ft vs 2.34 ft on everything else | breaking-ball popup rate, and whether opponent breaking usage stops climbing |
| **4** | Bat speed **up** 0.66 mph raw, +0.49 peer-netted; attack angle unchanged once peer-netted | **Strength & conditioning** | **De-prioritised again.** v1.0.0 ruled bat speed out from the outcome side; the path data rules it out from the input side. Two independent methods, same answer | — |
| **5** | Team-wide tilt drift of −1.1° to −1.2° across every cohort hitter (**O-16**) | **R&D / data plane** | Establish whether the 2025→2026 tilt shift is a real league trend or a Statcast calibration change. Until that is settled, **no year-over-year tilt number should be published without a peer control** | Savant methodology notes, or a league-wide replication |

Rows 1 and 2 are the same physical story at two grains, and they are what this addendum adds beyond
v1.0.0: **a flat plane with the contact point drifting away from the body.**

---

## §7 · Caveats and declared limits

1. **Two seasons, not a career.** Bat path begins in 2025. Nothing here can say what Turner's swing
   looked like during his 2020–21 peak, and the report never implies it.
2. **O-16 is unresolved.** The team-wide tilt drift may be a real trend or a calibration change. Every
   tilt claim here is peer-netted; the raw deltas ship beside them so the DPO can see both.
3. **O-15 inverts a published convention.** If a future consumer reads the MLB glossary onto
   `attack_direction`, every pull/oppo statement they make from this column will be backwards. Both the
   raw column and the corrected `pull_direction` ship in every receipt.
4. **The within-2026 breaking-ball popup contrast is 15 tracked balls in play.** Directionally consistent,
   statistically thin. It is reported with its sample and is not the load-bearing evidence.
5. **Popup counts differ by one or two between panels.** `popup_rate` (PU-2) uses **all** balls in play so
   it reconciles exactly with the v1.0.0 product; `popup_signature` (PU-1) uses **tracked, non-degenerate**
   balls in play, because a bat path is required. Both denominators ship; the reconciliation receipt
   asserts a maximum difference below 1×10⁻⁹ against v1.0.0.
6. **O-18: bunts and checked swings are excluded** from every bat-path central tendency and counted
   separately. This is a definitional exclusion, not a filter tuned to the result.
7. **O-17: `hyper_speed` is not used anywhere.** It is a deterministic transform of exit velocity.
8. **No causation.** §6 is hypotheses mapped to remit, as in v1.0.0.

---

*Receipts: `dp_uc40a_*.csv` (16 files) + `dp_uc40a_bp_headlines.json` · figures `dp_uc40a_fig1..4.png` (all four referenced above) ·
semantics, technical definitions and lineage in `03a_bat_path_semantics_and_lineage.md` · certification in
`05a_bat_path_certification.md` · independent verification `dp_uc40a_verification.py`.
uc-pos-014 **v1.1.0** · generated 2026-09-03 · Phillies Offense · Data Product Owner: Kellen Short.*
