# Claude Design brief: "Bryce Harper | 3 | The Eye Carried a Softer Bat"
### Bryce Harper 2026 season recap notecard · UC #61 · `uc-pos-025` · `dp_uc61` v1.0.0

> **For Claude Design.** Build a one-page notecard (and, later, animate it) from the pieces in this folder. Every number on the card is
> already written in `copy_notecard.json` or computable from the CSVs listed below; use those values exactly and invent none. Where this
> brief and your taste disagree on data, the brief wins; on type, layout and motion, use your judgment inside the tokens.

## 0 · What to make
- **One notecard**, landscape or portrait (reference: `ref_notecard_reference.png`, 2400 × 2844), four regions under one headline.
- **Headline (exact):** `Bryce Harper | 3 | The Eye Carried a Softer Bat` · dek: `2026 regular season · 162 G · 693 PA · .269/.380/.485 · 29 HR · .375 wOBA`.
- **TL-a · four bullets (exact text):**
1. **Still the Phillies' best bat.** .269/.380/.485 with 29 HR, and he appeared in all 162 games. His .375 wOBA led the 10 Phillies with 200+ PA and sits in the 94th percentile of 122 Phillies hitter seasons since 2015.
2. **The eye did the heavy lifting.** A 15.4% walk rate, his best since 2020, drove a .380 OBP. Chase (32.4%) and strikeouts (21.4%) stayed inside his Phillies range, and after the break he took even more pitches just off the plate (edge-take .411 → .446).
3. **The thump stepped back.** Hard-hit 42.8%, barrels 10.3%, 90th-percentile exit velocity 106.3 mph and a .485 SLG: all his lowest as a Phillie. After the break hard contact fell again (46.2% → 37.4%), and the walks held his OPS level (.862 → .868).
4. **Lefties were the leak.** Against righties, .997 OPS and 25 HR; against lefties, .657 and 4 HR, his lowest vs-LHP OPS in 12 Statcast seasons. The contact backs the results (xwOBA .314 vs wOBA .299): mostly earned, not bad luck.
- **TL-b · cumulative chart:** `2026 Ran Inside His Phillies Range Almost All Year`. Default metric wOBA. Offer a metric switch (wOBA / OPS / OBP / SLG / BA / HR) from
  `tl_cumulative_by_pa.csv`; the switch changes the y axis only.
- **TR · pitch maps:** `Righties Paid. Lefties Didn't.`. Two panels, **vs RHP** and **vs LHP**, each with its header and three callouts (`copy_notecard.json → pitch_map`).
- **B · spray chart:** `Pulling More, Hitting It Softer` with the KPI strip:

| KPI | 2026 | 2019–25 Phillies range |
|---|---|---|
| Hard-hit | 42.8% | 45.6%–50.7% |
| Barrel | 10.3% | 10.6%–18.1% |
| Line drive | 25.9% | 22.0%–29.7% |
| Pull | 49.9% | 43.4%–48.0% |
| Oppo | 25.6% | 28.4%–36.6% |
| Pull-air | 19.0% | 18.1%–20.4% |

## 1 · Non-negotiables (data fidelity)
1. **Regular season only.** No postseason anywhere.
2. **Cumulative x = plate appearances into the season**, not games or dates. One line per season, 12 seasons (2015–26). 2026 red and
   thickest; Phillies 2019–25 solid slate; Washington 2015–18 dashed and lighter; the 2019–25 min–max band is optional context.
   Rate lines start at PA 25 (`below_floor = true` rows are not drawn); HR is a step line from PA 1.
3. **The band ends at PA 620.** No earlier Phillies season reached 693 PA; never extrapolate it.
4. **Pitch maps are the catcher's view.** Zone rectangle half-width 0.83 ft, mean height 1.648–3.265 ft;
   the dotted shadow band sits one ball width (0.25 ft) outside it. Harper (LHB) stands on the **+x** side. Faint dots are location
   marks (not to scale); solid dots are `damage = true` (hard-hit 95+ mph or HR); stars are HR.
5. **Pitch-group colors carry meaning only in TR**, hit-type colors only in B, era colors only in TL-b. Label everything; never rely on
   color alone.
6. **Spray honesty.** Every park is drawn on one basic outline (the house CBP wall). Caption: "All 155 hits, every park, drawn on one outline". Home runs sit on their
   spray bearing at `hit_distance_sc`; other hits at their fielded point. 14 hits sit up to
   7.1° past a foul line: a fair ball down the line is often fielded in foul ground, and
   1 HR's bearing carries coordinate error. Draw them where they are; never move a ball.
7. **Small cells.** Lefty offspeed (18 PA) is drawn but never called out.
8. **No causal or medical claims.** The card says what happened, not why.

## 2 · Brand tokens
| Token | Value | Use |
|---|---|---|
| Surface / ink / secondary ink | `#FFFFFF` / `#1F2430` / `#5B6170` | page, titles and values, axes and notes |
| Phillies navy | `#002D72` | header band, reference line |
| Phillies red | `#E81828` | 2026 only in TL-b; fastballs in TR; HR in B |
| Era: Phillies 2019–25 / Washington 2015–18 | `#8C96A6` / `#C3C9D2` (dashed) | TL-b context |
| Pitch group: Fastballs / Breaking / Offspeed | `#E81828` / `#7A5CC7` / `#0E9384` | TR |
| Hit type: Single / Double / Triple / HR | `#2E6FB5` / `#0E9384` / `#7A5CC7` / `#E81828` | B; outs `#D5DAE1` |
| Type | Arial (Liberation Sans fallback), titles bold | |

## 3 · Motion ideas for the animation pass (optional, your call)
- **TL-b:** the 11 prior seasons draw together in slate, then 2026 draws in red at ≈ 1 s per 100 PA and lands on **.375**.
  The metric switch cross-fades the y axis.
- **TR:** faint dots fade in by month (`game_date`); damage balls pop in after; the three callouts type on per panel.
- **B:** hits land in date order; the KPI strip counts up to its final values once the last ball lands.

## 4 · Files
| File | Region | What |
|---|---|---|
| `copy_notecard.json` | all | headline, bullets, titles, callouts, caveats; `numbers` lists every printed number with its source key |
| `tl_cumulative_by_pa.csv` | TL-b | one row per PA, 2015–26: BA, OBP, SLG, OPS, wOBA, HR (`hr_count`), era, floor flag |
| `tl_career_envelope.csv` / `tl_season_endpoints.csv` | TL-b | per-PA band (Washington, Phillies) with seasons counted / end-of-season values |
| `tr_pitch_map_2026.csv` / `tr_zone_geometry.json` | TR | every 2026 pitch with location, group, swing/whiff, damage / zone drawing constants |
| `tr_platoon_2026.csv` / `tr_hand_by_pitch_group_2026.csv` / `tr_zone_damage_2026.csv` | TR | callout tables |
| `b_spray_2026.csv` / `b_field_outline.json` | B | every 2026 ball in play with plotted feet (`x_ft`, `y_ft`) / wall, foul lines, bases, infield arc |
| `ref_*.png` | all | audited reference pieces (V1–V7 PASS) and the composed reference card |
