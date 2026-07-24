# Advance Scout — Aaron Nola (RHP) vs the Los Angeles Dodgers
### Philadelphia vs Los Angeles · Citizens Bank Park · 2026-07-22 · home start · third extension of the Nola advance file (UC8 → UC15 → UC26)

**Prepared for:** manager / pitching coaches & analysts / catcher (Realmuto or Marchan) / Nola — advance meeting
**Throws:** R · **Arsenal:** 6 pitches (Knuckle Curve, Sinker, 4-Seam, Cutter, Changeup, Slider)
**Governance:** Use Case #26 (`uc-pps-021`). Every rate KPI is **inherited verbatim** from the locked UC8→UC11→UC15 line (get_stats/nresults, whiff, chase, putaway, FPSR, hard-hit) plus the **UC8 glossary-approved trio** (edge rate, out-of-zone called-strike rate, AIR/GB rate). **No new rate KPIs.** Recomputed live off `phils_2015..2026`, fresh through Nola's last start **2026-07-16**. Supersedes dp_uc15's season figures (earlier cache).

> ⚠️ **Read this first — data window & sample sizes.**
> - **Career log** = `data/phillies/phils_2015..2026.parquet`, entity-locked to **MLBAM 605400** (not Nolan Hoffman 676510), regular season only, deduped. Cache fresh through **2026-07-16** — Nola's most recent start (he starts tonight on 6 days' rest).
> - **Matchup scope = SEVEN named hitters by DPO decision** — not a posted 1–9 card: Betts, Ohtani, Freeman, Muncy, Tucker, Pages, Edman. **Confirm the actual lineup before first pitch.**
> - **H2H is career and small: 8–86 PA per hitter.** Only **Freeman (86 PA)** is a real sample; the rest (8–25 PA) are **directional** and printed with their PA. Most last faced Nola in **April 2025** — they predate his 2026 shape.
> - **Season wOBA is FanGraphs-weighted** (the locked KPI); it reads ~.01 below the Statcast `woba_value` line. **xwOBA here means xwOBAcon** (mean estimated wOBA on balls in play) — a data-quality fix made this session; the pitch-level `get_stats.xwoba` column is contaminated and is **not** cited.

---

## Bottom line

1. **The two-year slide is still sliding — but it isn't the stuff.** 2026 sits at **.358 wOBA / .509 SLG / 5.1% HR per PA**, all career worsts. Velocity is flat (4-seam 92.3, no decline) and the strikeout rate is steady (23.8%). This is a **contact-in-the-air** problem, not injury or arm strength.
2. **The left-handed problem, sharpened to one number.** Contact quality is **identical by side** — xwOBAcon **.382 vs LHB / .387 vs RHB**, whiff **28.3% / 26.8%**. The *entire* lefty gap is **the free pass: 10.7% walk rate vs LHB against 2.8% vs RHB**, on **58.8% first-pitch strikes vs 73.5%**. He nibbles lefties into hitters' counts and pays for it. **This lineup stands five left** (Ohtani, Freeman, Muncy, Tucker, and switch-hitter Edman).
3. **Don't blame the zone.** Edge rate **.370** (career norm .374), out-of-zone called strikes **.034** (a slow decade glide — 2025 was already .038, this is not a 2026 ABS cliff), chase-up rate **.311** (career-high area). The fix is sequencing and conviction, not the umpire.
4. **One real positive to build on: the changeup woke up.** It now misses bats at **26.9% vs LHB** (up from ~16% at UC8) and he has leaned in — **19.4% usage vs LHB, up to 21% staff-wide in July.** Paired with the **42.5%-whiff knuckle curve**, he finally has a two-pitch finish to lefties — *if he'll throw them in the zone.*
5. **The matchup: Betts is the danger; Freeman is the book; the rest are a manageable, familiar plan.** Mookie Betts has squared him (**.465, 2 HR / 23 PA**); Freeman is the volume history (**.307 / 86 PA**, patient). The plan is the one he executed at KC on **7/05 — 7 IP, 0 BB, 0 HR, 7 K**: get ahead of the lefties, finish with curve and changeup, keep the fastball out of the air.

---

## The profile — a fourth straight step down, but the engine is contact

| Season | GS | PA | wOBA | xwOBAcon | K% | BB% | HR/PA | SLG |
|---|---|---|---|---|---|---|---|---|
| 2022 | 32 | 809 | .262 | .343 | 29.0% | 3.5% | 2.3% | .346 |
| 2023 | 32 | 792 | .303 | .374 | 25.1% | 5.7% | 4.0% | .426 |
| 2024 | 33 | 822 | .309 | .371 | 23.8% | 6.1% | 3.6% | .420 |
| 2025 | 17 | 406 | .344 | .400 | 23.9% | 6.9% | 4.4% | .477 |
| **2026** | **20** | **453** | **.358** | **.384** | **23.8%** | **7.5%** | **5.1%** | **.509** |

The **.358** is the worst full-season wOBA of his career, and **SLG (.509)** and **HR rate (5.1%)** are career worsts alongside it. But read the rest of the row before you reach for an alarm: **the strikeouts haven't moved (23.8%)** and **the velocity is intact** — nothing in the arsenal has lost a tick. Even xwOBAcon (.384) is a hair *below* 2025's .400, so 2026 is not a contact-quality cliff *beyond* where 2025 already was. What has grown is the **walk rate (7.5% — his highest since 2019)** and the **home-run rate (a career-worst 5.1%)** — free passes and balls in the air. This is a command-and-sequencing season, not a stuff-decline season.

![Contact-quality engine](out/dp_uc25_contact_quality.png)

---

## Kept current — the three starts since the last report

The advance file was last refreshed at dp_uc15 (through 7/04). Three starts have landed since:

| Date | Opp | Venue | IP* | Pitches | PA | H | HR | BB | K | wOBA |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-05 | KC | road | 7.0 | 98 | 28 | 7 | 0 | 0 | 7 | **.249** |
| 2026-07-10 | DET | road | 5.0 | 84 | 20 | 3 | 1 | 2 | 8 | **.280** |
| 2026-07-16 | NYM | home | 6.0 | 101 | 27 | 6 | 3 | 3 | 6 | **.404** |
| **Last-3 combined** | | | | **283** | **75** | **16** | **4** | **5** | **21** | **.313** |

*\*IP computed from terminal events in the pitch log, not box scores.*

The three-start line (**.313 wOBA, .329 xwOBAcon, 75 PA**) is a tick better than the season — and the **7/05 game is a proof of concept**: it's the exact KC lineup dp_uc15 flagged ("six of nine have homered off him"), and Nola answered with **7 innings, zero walks, zero homers, seven punchouts.** When he pounded the zone and finished with the breaker, the plan worked.

**But be honest about the most recent look:** on **7/16 he gave up three home runs** to the Mets — same failure mode, balls in the air — and walked three. The trend is encouraging; the problem is **not solved.** Two good starts and a three-homer clunker is a pitcher who is *capable of* the game plan, not one who has locked it in.

![Results by start and pitch mix over time](out/dp_uc25_recency_approach.png)

---

## The arsenal — six pitches, one weapon, and a changeup that woke up

| vs | Pitch | Usage | Velo | Whiff% | Role |
|---|---|---|---|---|---|
| **LHB** | Knuckle Curve | 34.4% | 78.1 | **42.5%** | the putaway — below the zone, both sides |
| | 4-Seam | 26.7% | 92.3 | 13.8% | get-ahead, up — **the pitch that gets lifted** |
| | Changeup | 19.4% | 85.6 | **26.9%** | **the improved weapon** — fading away |
| | Sinker | 13.7% | 91.7 | 10.9% | back-door / in |
| | Cutter | 5.6% | 86.1 | 29.7% | in on hands — underused |
| **RHB** | Knuckle Curve | 34.0% | 78.4 | 38.7% | the putaway — below the zone |
| | Sinker | 29.9% | 91.5 | 14.1% | the anchor — glove-side, ground balls |
| | 4-Seam | 18.0% | 92.1 | 15.9% | get-ahead, up |
| | Cutter | 10.4% | 86.0 | 26.8% | in on hands |
| | Changeup | 5.0% | 85.3 | 28.6% | show |
| | Slider | 2.7% | 83.0 | 25.0% | RHB-only experiment (19 thrown all year) |

The **knuckle curve is still the whole identity** — a third of the pitches to both sides and the only bat-misser that clears 38%. The 2026 wrinkle to righties is the **sinker at 30%**, pounded glove-side for grounders. And the news vs lefties is the **changeup**: at UC8 (June) it was his designated LHB weapon getting only ~16% whiff; across the full season it's up to **26.9%**, and his July usage spiked to 21%. He's earned the right to throw it more. The weak spot that remains is the **4-seam to lefties (13.8% whiff)** — the get-ahead fastball that, left up, becomes the air-ball damage.

![Arsenal map by stand](out/dp_uc25_nola_arsenal_map.png)

![Usage vs whiff by pitch](out/dp_uc25_usage_whiff_2026.png)

---

## The left-handed problem — down to the indicator

This is the report. Same wOBA both sides; the *mechanism* is what separates them.

| 2026 process | vs LHB | vs RHB |
|---|---|---|
| Plate appearances | 272 | 181 |
| wOBA | .361 | .353 |
| **xwOBAcon** | **.382** | **.387** |
| **Walk rate** | **10.7%** | **2.8%** |
| Strikeout rate | 23.2% | 24.9% |
| **First-pitch-strike rate** | **58.8%** | **73.5%** |
| Put-away rate (2-strike) | 18.6% | 23.1% |
| Whiff rate | 28.3% | 26.8% |
| Chase rate | 32.5% | 32.9% |
| Hard-hit rate | 42.7% | 35.4% |

He **misses bats at the same rate** to both sides (28% / 27%) and gives up **the same contact quality** (xwOBAcon .382 / .387). The only levers that move are the ones he controls: he throws a **first-pitch strike 15 points less often to lefties (58.8% vs 73.5%)**, so he **finishes them less (18.6% putaway vs 23.1%)**, so he **walks them nearly four times as often (10.7% vs 2.8%).** The .361 lefty wOBA is a **sequencing tax he imposes on himself** — and tonight's lineup makes him pay it five times through the order.

![The ABS re-test and the L/R process split](out/dp_uc25_process_abs_panel.png)

---

## The ABS question — asked again, same answer

UC8 tested whether the automated zone was the cause of the slump. Re-tested with data through 7/16, the answer holds:

- **Edge command is intact.** Edge rate **.370** in 2026, within a whisker of the **.374** career norm.
- **The "stolen strike" is a slow decade decline, not a 2026 cliff.** Out-of-zone called strikes fell from **~.088 (2015)** to **.034 (2026)** — but **2025 was already at .038.** An ABS-driven break would show a step-down *this* year; instead it's a nine-year glide.
- **He still generates chase up.** Chase-up rate **.311**, near his career high — hitters keep expanding above the zone.

The takeaway for the dugout is a *negative* one: don't spend a meeting on the zone. The two things the data flags are the **lefty free pass** and the **air-ball contact** — both self-correctable.

---

## The contact-quality engine

| Batted-ball KPI (BIP) | 2024 | 2025 | 2026 | career-worst? |
|---|---|---|---|---|
| Ground-ball rate | 44.6% | 42.9% | **40.3%** | ✔ lowest |
| Air-ball rate | 55.4% | 57.1% | **59.7%** | ✔ highest |
| Hard-hit rate (≥95) | 38.2% | 43.3% | 39.6% | — (2025 worse) |
| HR rate (per PA) | 3.6% | 4.4% | **5.1%** | ✔ highest |
| xwOBAcon | .371 | .400 | .384 | — (2025 worse) |

Nola has always been a ground-ball-leaning contact manager. In 2026 **more balls are in the air (59.7%, a career high) and more are leaving the yard (5.1% HR, a career high).** Hard-hit and xwOBAcon actually eased slightly off 2025 — so the incremental 2026 damage is specifically **the air-ball/home-run channel.** Keeping the ball down isn't a preference tonight; it's the entire run-prevention plan.

---

## The Dodgers — the seven-hitter file

Career head-to-head from Nola's own log (name-parsed; **small samples — PA shown on every line**). Five of the seven stand left vs a RHP.

| Hitter | Stands | PA | H | HR | BB | K | Whiff% | wOBA | xwOBAcon | Read |
|---|---|---|---|---|---|---|---|---|---|---|
| **Mookie Betts** | R | 23 | 9 | 2 | 0 | 5 | 21% | **.465** | .555 | **DANGER** — has squared him |
| **Freddie Freeman** | L | 86 | 18 | 2 | 10 | 11 | 18% | .307 | **.397** | **WATCH** — the real book, patient |
| Shohei Ohtani | L | 9 | 1 | 0 | 1 | 3 | 44% | .216 | **.450** | **DANGER** (talent + loud contact) |
| Max Muncy | L | 25 | 4 | 0 | 1 | 11 | 30% | .184 | .362 | EXPLOIT — 11 K in 25 PA |
| Andy Pages | R | 8 | 1 | 0 | 0 | 3 | — | .157 | .287 | directional — thin book |
| Tommy Edman | L (S) | 19 | 1 | 0 | 0 | 0 | 9% | .065 | .240 | EXPLOIT — weak contact |
| Kyle Tucker | L | 8 | 0 | 0 | 0 | 1 | — | .000 | .230 | directional — no real book |

![Career wOBA vs Nola — the seven](out/dp_uc25_dodgers_h2h_matrix.png)

**The plans (H2H-driven where the PA supports it, profile-driven where it doesn't):**

- **Mookie Betts (R, 23 PA, .465, 2 HR).** The one Dodger who has genuinely hit him, and the contact is loud (.555 xwOBAcon). **Sinker glove-side at the knees, knuckle curve to the chase zone below — nothing middle, nothing he can extend on.** Pitch backward; don't let him sit in a hitter's count.
- **Freddie Freeman (L, 86 PA, .307, 10 BB).** The only large sample, and the archetype of Nola's leak — a patient lefty who **won't chase and will take the walk (10 in 86 PA).** The wOBA says "handled," but **xwOBAcon .397 says the contact is loud when he does connect.** Pound the zone early; make him hit the curve or changeup down, not ball four.
- **Shohei Ohtani (L, 9 PA — directional).** The line is empty (3 K, .216) but the **.450 xwOBAcon over even 9 PA plus his talent = treat him as danger, full stop.** Never a fastball he can elevate; curve and changeup down, and **do not walk him into the Freeman/Muncy pocket.**
- **Max Muncy (L, 25 PA, .184, 11 K).** Nola has owned him — **11 strikeouts in 25 PA.** All-or-nothing lefty; **bury the knuckle curve, he'll chase it.** Don't groove a get-me-over cutter.
- **Tommy Edman (switch → L, 19 PA, .065, 9% whiff).** Handled — a contact bat Nola has kept off the barrel. Standard lefty plan; keep it down so he can't slap a fastball.
- **Andy Pages (R, 8 PA — directional) / Kyle Tucker (L, 8 PA — directional).** No real book on either. **Pages:** righty plan — sinker/curve, expand with two strikes. **Tucker:** left-handed plan — get ahead, curve and changeup away, keep the 4-seam out of the air (he's the highest-ceiling bat here without a track record vs Nola — respect the profile, not the 0-for-8).

### The single attack rule
**Get ahead of the five lefties, and finish them with the curve and the changeup — never a fastball they can lift.** Everything Nola's leak costs him is a walk; everything this lineup does to him is in the air. Win the first pitch and keep the ball down, and the Dodgers are a manageable night.

---

## Game-plan takeaways — by persona

1. **Nola — attack the zone first-pitch to lefties.** The **10.7% lefty walk rate** is the whole leak, and it starts at **58.8% first-pitch strikes** (73.5% to righties). First-pitch curve or sinker for a strike; save the chase pitches for two strikes. You don't need to be *fine* to this lineup — you need to be *ahead*.
2. **Catcher (Realmuto or Marchan) — call the two-pitch lefty finish.** Knuckle curve down (**42.5% whiff**) and changeup away (**26.9%, and warming**) are the putaway pair. **The two-strike pitch to a lefty is never a 4-seam middle** (13.8% whiff, and it's the air-ball pitch). With Marchan likely behind the plate and Stubbs out, keep the target below the zone with two strikes and make Nola commit to the breaker.
3. **Pitching coach / analyst — reinforce the changeup, and script the third time through.** The changeup-vs-LHB jump (16%→27% whiff) is real; keep feeding it. And the damage this year clusters as the lineup turns over — his four .40+ wOBA starts in June and the **7/16 three-homer game** all came late. Have the hook conversation ready for the Betts/Ohtani/Freeman pocket the third time.
4. **Manager — leash by matchup, not pitch count.** ~95–100 pitches is the range, but the trigger is the **third pass through the lefty top**, not a round number. The bullpen lever tonight is that lefty core — have a left-hander warm for the **Ohtani/Freeman/Muncy** stretch if Nola's first-pitch-strike rate to them is sagging.
5. **Nola / catcher — pick your spots to pitch backward.** **Betts** is the only Dodger who's beaten him and **Ohtani** is the only other with a loud contact-quality signal on a thin sample. Those two get the pitch-backward treatment; **everyone else is get-ahead-and-expand.**
6. **Analyst / advance desk — confirm the card and refresh if needed.** This file is **seven named hitters, not a posted 1–9.** Confirm the actual lineup before first pitch, and re-run `dp_uc25_nola_vs_dodgers.py` if a 21st start lands or the lineup firms up.

---

## Candid data-window & freshness caveats

- **Pre-game projection.** Tonight's game is not — and cannot be — in any cache. Nothing here reflects in-game data.
- **Matchup = 7 named hitters (DPO scope),** not a confirmed 1–9. The L/R math (5 lefties) depends on the actual card; confirm it.
- **H2H is career and small (8–86 PA)** and reconstructed from Nola's own log via des-parsed batter ids. **Only Freeman (86 PA) is a real sample;** the rest are directional. Most last faced Nola in **April 2025** and predate his 2026 pitch shape. **Betts .465/23 PA** and **Ohtani .450 xwOBAcon/9 PA** are flags, not forecasts.
- **Season wOBA is FanGraphs-weighted** (the locked KPI), ~.01 under the Statcast `woba_value` line; it **supersedes dp_uc15's .377** (that was an earlier cache, closer to the Statcast side). **xwOBA = xwOBAcon on balls in play** — a data-quality correction made this session, because the locked `get_stats.xwoba` pitch-level column is contaminated by non-BIP rows and is not fit to cite.
- **IP on game lines is computed** from terminal events in the pitch log, not official box scores (marked with an asterisk); pitch counts and PA-level results are exact.
- **Results vs process, said plainly:** the last-3 **.313 wOBA** sits on a **.329 xwOBAcon** — real recent improvement — but the **7/16 three-homer start** says don't declare victory. The lefty wOBA gap, by contrast, is **process (walks), not contact** — which is exactly why it's fixable tonight.
- **Artifact pointers:** build script `dp_uc25_nola_vs_dodgers.py`; receipts `out/dp_uc25_*.csv` / `.png`; governance trail `dp_uc25_nola_vs_dodgers_use_case_spec.md`; independent verification `dp_uc25_verification.py`.

---

*Source: governed Phillies Pitching data product, UC#26 (`uc-pps-021`). Nola pitcher-side from `data/phillies/phils_2015..2026.parquet` (regular season, `pitcher==605400`), fresh through 2026-07-16. Dodgers head-to-head from the same log filtered to the seven named hitters (des-parsed ids). Locked KPIs inherited verbatim from the UC8→UC11→UC15 line; edge rate / OOZ called-strike rate / AIR-GB rate inherited from UC8. Pattern lineage UC3 → UC6 → UC8 → UC11 → UC15 → UC26.*
