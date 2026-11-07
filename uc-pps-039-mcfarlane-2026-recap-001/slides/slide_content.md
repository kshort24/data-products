# Slide content · Alex McFarlane | 2026 | Nasty Stuff, Outlier Heater

Built for Claude Design. Each slide: the client's words (commentary, verbatim; † = registered correction), the numbers that may appear on screen (each registered in `copy_registry.json`), the visual and its data, an animation cue, and a data note for the speaker.
Rules for the build: every number on a slide must come from `copy_registry.json` or a file in `data/`; keep the † marks; no team logos, player photos or headshots; Phillies red #E81828 = McFarlane, navy #002D72 = Kerkering / structure, gray = context.

---
## Slide 1 · Alex McFarlane | 2026 | Nasty Stuff, Outlier Heater

**Commentary (on screen or voice-over).** Nasty stuff.

**On-screen numbers.** 333 pitches · 21 outings · .280 wOBA · 99.4 mph · 2544 rpm

**Visual.** Title card. Big type over a four-seam trail.

**Data.** `data/dp_uc63_headlines.json`

**Animation cue.** A radar-gun readout counts 0 → 99.4 while the spin readout counts 0 → 2544; the headline sets on the last tick.

**Speaker's data note.** 333 pitches · 21 outings (2 postseason) · .280 wOBA · 26% K · 8.2% BB · four-seam 99.4 mph / 2544 rpm

---
## Slide 2 · Hand-in-hand

**Commentary (on screen or voice-over).** Time to recap Alex McFarlane's 2026 season. Frankly, it has to go hand-in-hand with the guy who was drafted in the round following McFarlane back in 2022. A fellow right-handed college reliever from Florida, Orion Kerkering. Taken in the 5th round out of South Florida†, Kerk was rushed to the majors back in 2023 to pitch in leverage situations for several iterations of this ballclub.

**On-screen numbers.** 2022 · Rd 4 · Miami · 2022 · Rd 5 · South Florida†

**Visual.** Two draft cards side by side (no logos, no photos).

**Data.** carry-ins only (see BID HP-11)

**Animation cue.** Card one flips (McFarlane, Rd 4), then card two (Kerkering, Rd 5); a dotted line joins them: 'the round following'.

**Speaker's data note.** Both 2022 draftees out of Florida colleges (McFarlane, 4th round, Miami; Kerkering, 5th, South Florida). Kerkering's first 21 MLB outings ran 2023-09-24 to 2024-05-13 and included 7 postseason games; McFarlane's ran 2026-07-22 to 2026-09-30 with 2. HP-11b corrects the school.

---
## Slide 3 · Time to ascend

**Commentary (on screen or voice-over).** Now it was Alex McFarlane's time to ascend to the big league bullpen. During the fateful weekend in Atlanta which cost Rob Thomson his job, Alex McFarlane sat in the Phillies bullpen. Ready to be used. He was not needed.

**On-screen numbers.** Apr 24 · recalled from AA Reading · Apr 28 · Thomson dismissed · Jul 20 · recalled again · 07-22 · MLB debut

**Visual.** Horizontal 2026 timeline, April to October.

**Data.** `data/dp_uc63_stint_ledger.csv`

**Animation cue.** The timeline draws left to right. At the Atlanta weekend a bullpen chair lights up and stays empty ('He was not needed'). The line jumps to July and the first pitch lands on 7/22.

**Speaker's data note.** Recalled from Double-A Reading on 4/24 before the Atlanta series; Thomson was dismissed 4/28 (carry-ins CI-1, CI-2). The log has no McFarlane pitch until 2026-07-22: he sat, and was not needed.

---
## Slide 4 · 333 pitches, 21 outings

**Commentary (on screen or voice-over).** McFarlane dominated AA for most of 2026, I do not have statcast data for that. I do have data from his brief stint in AAA along with all 333 of his major league pitches across 21 outings including two postseason games.

**On-screen numbers.** MLB · 1 outing · AAA · 4 outings · 8 K / 2 BB · MLB · 20 outings · 2 Wild Card games

**Visual.** Three stint blocks (MLB → AAA → MLB) sized by pitches.

**Data.** `data/dp_uc63_stint_ledger.csv`, `data/dp_uc63_aaa_outings.csv`, `data/dp_uc63_outing_ledger.csv`

**Animation cue.** A pitch counter runs 0 → 333 as the MLB blocks fill; the AAA block fills in a muted tone (supporting tier) and is never added to the count.

**Speaker's data note.** AAA is a supporting tier: 4 Lehigh Valley outings 2026-07-29 to 2026-08-08, 73 pitches, 8 K and 2 BB in 17 PA, 32% whiffs. Stints: MLB debut 2026-07-22 (12 pitches), AAA, then MLB from 2026-08-11 through the Wild Card. MLB evidence: 333 pitches, 21 outings (19 regular season + 2 Wild Card).

---
## Slide 5 · The Bridge to Duran

**Commentary (on screen or voice-over).** McFarlane emerged as a key plank in the Bridge to Duran, the highwire act conducted by Don Mattingly when protecting a lead down the stretch for this ballclub. McFarlane's presence in the "Circle of Trust" belied his inexperience. His eye-popping stuff plays against big league hitters. Improved command in 2026 brought improved results with solid underlying metrics.

**On-screen numbers.** 4 bridge outings · first 08-31 · lead intact 3 of 4

**Visual.** F6 bottom panel: lead at entry by date; diamonds = bridge outings.

**Data.** `data/dp_uc63_outing_ledger.csv`, `ref/dp_uc63_f6_outings.png (+ .json plotly spec)`

**Animation cue.** Gray dots for every outing appear in date order; at 8/31, 9/6, 9/9 and 9/27 a red diamond pops and a dashed arrow runs to a 'DURAN' marker on the right.

**Speaker's data note.** BD-1: 4 of 19 regular-season outings came with a lead and Duran to follow, the first on 2026-08-31; he left with the lead intact in 3 of 4. He entered with the lead 9 times. 'Emerged … down the stretch' fits; 'key plank' is ahead of four outings (PARTLY). Command can't be compared to a prior year (no pre-2026 pitch data; NOT OBSERVABLE).

---
## Slide 6 · His overall year

**Commentary (on screen or voice-over).** First we take a look at his overall year. He pitched to a .280 wOBA (good!) and .633 OPS (solid!). Decent chunk of hard hits and barrels, but very strong whiff in total and good chase. Pointing to quality stuff. 26% K and 8.2% BB are good. The ratio just exceeding 3:1 is quite good.

**On-screen numbers.** .280 wOBA · .633 OPS · 26% K · 8.2% BB · 22:7 K:BB

**Visual.** F1: six context boxes (Phillies pitcher-seasons since 2015) with his red dot.

**Data.** `data/dp_uc63_overall.csv`, `data/dp_uc63_context_percentiles.csv`, `data/dp_uc63_context_pool_cx1.csv`, `ref/dp_uc63_f1_context.png (+ .json plotly spec)`

**Animation cue.** Boxes rise from the axis one metric at a time; the red dot drops into each and its percentile label types on.

**Speaker's data note.** Exact: .280 wOBA, .633 OPS, 25.9% K, 8.2% BB, 22:7 K:BB. Against 258 Phillies pitcher-seasons since 2015 (regular season only): whiff 27.9% = 73rd pct, chase 31.7% = 74th, hard-hit 40.4% (pool median 35.7%). xwOBA .299 sits a touch above the .280 wOBA: results ran slightly ahead of contact quality.

---
## Slide 7 · The pitch plot

**Commentary (on screen or voice-over).** Then we look at his pitch plot which is... hard to contextualize. Lots of FF that ride between 12 and 18 inches and run about 9 inches†. His sinker runs up to 18 inches. Bullet slider angles nicely off his FF which likely explains the deception to lefties. Speeds them up with heaters up and out over the plate. Follows that with a hammer slider that looks the same out of the hand before falling off the table. Sweeper sweeps at least a foot but is fairly flat, but can tunnel off his sinker when on.

**Chart subtitle (client's).** Velocity is stronger than shape in his Stuff model

**On-screen numbers.** FF 13–17 in ride · 9.5 in run · SI 16.4 in run · ST 12.9 in sweep

**Visual.** F2: every pitch, horizontal vs induced vertical break (inches), gray Phillies RHP context.

**Data.** `data/dp_uc63_pitches.csv`, `data/dp_uc63_arsenal_shapes.csv`, `data/dp_uc63_pitch_type_pool_rhp.csv`, `ref/dp_uc63_f2_pitch_plot.png (+ .json plotly spec)`

**Animation cue.** Pitches fly in by type in the order of the commentary: FF (red, ride up), SI (orange, runs arm side), SL (yellow, angles off the FF), ST (gold, sweeps). Keep the gray context fixed underneath.

**Speaker's data note.** FF: 12.9–16.5 in of ride (10th–90th pct), 9.5 in of run (median). SI: 16.4 in of run, 18.6 in at the 90th pct. SL: 4.7 in sweep, -2.0 in IVB (bullet-adjacent: BS-1r draws the line at 4.0 / 4.0). ST: 12.9 in sweep, 2.3 in IVB. The log tags one slider (SL, 70 pitches, IVB -4.7 to 1.2 in): the 'bullet' and the 'hammer' are one pitch type here. FF to lefties: 42% upper third or above the zone. The Stuff-model subtitle is the client's read (no stuff model in the plane).

---
## Slide 8 · Pitch maps

**Commentary (on screen or voice-over).** Now we look at pitch maps to gauge approach against left-handed batters and right-handed batters. Callouts at the stand level include: Against LHB, quality K Rate (33%) and Elite Walks Rate (2.6%)†. While against RHB: Diverse pitch mix | Just .179 BAA but lots of hard contact in the underlyings (41.9% HH, 9.7% Barrel)†.

**Chart subtitle (client's).** vs LHB: 63.4% FF + 27.5% SL | Elite K Rate (33%) and Limits Walks (2.6% BB Rate)†  |  vs RHB: 45.6% SI + 25% FF + 15.6% SL + 13.9% ST | Just .179 BAA but lots of hard contact in the underlyings

**On-screen numbers.** vs LHB K 33% · BB 2.6%† · vs RHB .179 BAA · 41.9% HH† · 9.7% barrel†

**Visual.** F3: catcher's view, two panels (vs LHB, vs RHB); bubble = mean location, size = usage; faint dots = every pitch.

**Data.** `data/dp_uc63_pitch_map_mix.csv`, `data/dp_uc63_pitches.csv`, `data/dp_uc63_by_stand.csv`, `ref/dp_uc63_f3_pitch_map.png (+ .json plotly spec)`

**Animation cue.** LHB panel first: the zone draws, faint pitches sprinkle in, then the FF and SL bubbles inflate to 63.4% and 27.5%. Then the RHB panel: SI inflates to 45.6% and the four-pitch mix spreads.

**Speaker's data note.** vs LHB 39 PA: K 33.3%, BB 2.6% (1 walk). vs RHB 46 PA: BAA .179, HH 41.9%, barrel 9.7%, and 6 of his 7 walks (BB 13.0%).

---
## Slide 9 · His pitches against each batter handedness

**Commentary (on screen or voice-over).** So then we look at his pitches against each batter handedness. Plus SL to LHB: 38% Whiff/50% Chase. FF gets 32% Whiff on Swings to RHB. (33% whiff vs LHB).

**On-screen numbers.** SL v LHB 38% whiff · 50% chase · FF v RHB 32% · FF v LHB 33%

**Visual.** F4: whiff rate by pitch; gray boxes = Phillies RHP pitch-type seasons; blue = vs LHB, red = vs RHB, size = swings.

**Data.** `data/dp_uc63_stand_pitch.csv`, `data/dp_uc63_pitch_type_pool_rhp.csv`, `ref/dp_uc63_f4_stand_pitch.png (+ .json plotly spec)`

**Animation cue.** Boxes first; then the SL-vs-LHB dot rises to 38% and pulses; then both FF dots rise together (32% / 33%).

**Speaker's data note.** SL v LHB 38.1% whiff on 21 swings, 50.0% chase; FF v RHB 32.0% (25 swings), v LHB 33.3% (48). Every cell is under 50 swings: directional. The sinker to righties draws contact (5.3% whiff, 38 swings).

---
## Slide 10 · The outlier fastball

**Commentary (on screen or voice-over).** Which is indicating that he has an outlier fastball. So we build a graph to contextualize against other right-handed four-seam fastballs either thrown by Phillies pitchers or to Phillies batters since 2015. McFarlane has elite spin and elite velocity. His fastball is an outlier.

**Chart subtitle (client's).** Alex McFarlane throws an outlier Four-Seam Fastball

**On-screen numbers.** velocity 99th pct · spin 97th pct · 0 seasons up-and-right

**Visual.** F5 (the client's chart): every RHP four-seam in a Phillies game since 2015, velocity vs spin with marginals; then F5b: pitcher-season averages.

**Data.** `data/dp_uc63_fo1_pitch_sample.csv`, `data/dp_uc63_fo1_pool.csv`, `data/dp_uc63_fo1.json`, `ref/dp_uc63_f5_velo_spin.png (+ .json plotly spec)`, `ref/dp_uc63_f5b_fo1.png (+ .json plotly spec)`

**Animation cue.** The gray cloud fades in (137,203 pitches, drawn as a 20,000 sample). The red cluster lands top-right. Cut to the season averages: dots settle, McFarlane's lands last, and a dotted box opens up-and-right of him — empty.

**Speaker's data note.** FO-1: 99.4 mph (99th pct, #3 of 239 pitcher-seasons) and 2544 rpm (97th pct, #6). No other RHP four-seam season thrown in a Phillies game since 2015 (≥ 100 FF) sits at or above him on both. Pitch level: 0.3% of 137,203 righty four-seamers beat his average velocity and spin together.

---
## Slide 11 · Down the stretch

**Commentary (on screen or voice-over).** (No client sentence. Organization addition: the heater by outing.)

**On-screen numbers.** 100.0 mph first 16 · 98.1 mph last 3

**Visual.** F6 top panel: four-seam velocity per outing (time on x).

**Data.** `data/dp_uc63_outing_ledger.csv`, `ref/dp_uc63_f6_outings.png (+ .json plotly spec)`

**Animation cue.** Dots appear outing by outing on a running clock; the last three regular-season dots settle lower; the two Wild Card dots (open circles) bounce back.

**Speaker's data note.** Down the stretch the heater came down a tick: four-seam 100.0 mph in his first 16 regular-season outings, 98.1 in the last 3 (sinker 99.4 → 98.0); 99.6 in the Wild Card. Descriptive, not graded.

---
## Slide 12 · Stretch S-1: draft-class twins

**Commentary (on screen or voice-over).** (Organization's stretch, posed and built. Pairs with the client's opening paragraph.)

**On-screen numbers.** McFarlane .280 wOBA · Kerkering .258 · K 25.9% vs 23.5% · HH 41.1% vs 25.5% · postseason 2 vs 7

**Visual.** S1: first 21 MLB outings each; gray boxes = Phillies relief seasons; red circle = McFarlane, navy square = Kerkering.

**Data.** `data/dp_uc63_s1_twins.csv`, `data/dp_uc63_s1_mix_mcfarlane.csv`, `data/dp_uc63_s1_mix_kerkering.csv`, `ref/dp_uc63_s1_twins.png (+ .json plotly spec)`

**Animation cue.** Both markers start at the left edge and walk metric by metric; where they split (chase, hard-hit) the gap draws as a bracket.

**Speaker's data note.** S-1 (posed by the org, built): through 21 MLB outings each, McFarlane .280 wOBA / .299 xwOBA, 25.9% K, 8.2% BB, 41.1% hard-hit, 99.4 mph four-seam; Kerkering .258 / .277, 23.5% K, 10.6% BB, 25.5% hard-hit, 97.6 mph. Kerkering arrived into October (7 of his first 21 were postseason); McFarlane arrived into a pennant race (2). McFarlane missed more bats and walked fewer; Kerkering allowed far softer contact.

---
## Slide 13 · The ledger

**Commentary (on screen or voice-over).** (Closing slide: what the data confirmed in the narrative, and what it corrected.)

**On-screen numbers.** 11 confirmed · 7 partly · 1 corrected · 1 not observable

**Visual.** Claims table: client sentence, verdict, correction.

**Data.** `data/dp_uc63_hp_grades.csv`

**Animation cue.** Rows check off one by one; the corrected row (Central → South Florida) flips.

**Speaker's data note.** Bars were filed in the BID before any grade was computed. † marks a registered correction on every slide.
