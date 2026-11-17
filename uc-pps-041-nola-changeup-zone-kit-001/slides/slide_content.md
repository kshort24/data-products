# Slide content · Aaron Nola | 2026 | The changeup, in the zone

Built for Claude Design as the **closer to the client's video** (28 clips, 7 s each, of Nola changeups taken for strikes in zones 7–9).
Each scene: on-screen copy (every string registered in `copy_registry.json`), the visual and its data, an animation cue, and a speaker note.
Rules: every number on screen comes from `copy_registry.json` or `data/`; no logos, photos or likenesses; Phillies red #E81828 = the 28 / Nola 2026; gray = context.
Target: 16:9, 1920×1080, dark background (#0b1220) so it cuts cleanly from the video. Total ≈ 35–45 s.

---
## Scene 1 · The handoff from the video (≈ 4 s)
**On screen.** 28 changeups · bottom third · taken for strikes · 27 regular season + 1 Wild Card · None with two strikes
**Visual.** Type only, over the last video frame dimming to the dark background.
**Data.** `data/dp_uc65_headlines.json` (`cz1`, `cz1_r`, `cz1_post`)
**Animation cue.** A counter ticks 1 → 28 in sync with the last clip fading; "None with two strikes" sets last.
**Speaker's data note.** The 28 clips in the folder reconcile exactly to the data: 27 regular-season pitches and 1 from Wild Card Game 3 (10/01). No spring-training pitch qualifies.

---
## Scene 2 · The pitch map (hero, ≈ 12 s)
**On screen.** 489 MLB changeups in 2026 · 28 in the video · vs LHB · 25 of the 28 · vs RHB · 3 of the 28 · 8 of the 28 are centered just below the line — the ball only has to clip the zone · 86.0 mph average
**Visual.** Two catcher's-view panels (vs LHB | vs RHB), strike zone 3×3 with the bottom row (zones 7–9) tinted red, home plate below. Every pitch is a **baseball-sized circle (diameter 2.9 in = 0.242 ft in plate coordinates)**. Reference: `ref/dp_uc65_r1_pitch_map.png` (+ `.json`). Alternate raw-height view: `ref/dp_uc65_r2_pitch_map_raw.png`.
**Data.** `data/dp_uc65_pitchmap_2026.csv` (489 rows; `plate_x`, `plate_z_n` = height scaled to the hitter's zone on a 1.5–3.5 ft standard zone, `cz1` = in the video), `data/dp_uc65_cz1_28.csv` (the 28 in date order, `video_order` 1–28).
**Animation cue.** (1) Zone grid draws; bottom row tints red. (2) The 461 gray balls rain in fast (≈ 2 s), low alpha. (3) The 28 red balls land one at a time in `video_order` (date order), each with a small white flash ring; a counter in the corner ticks to 28. (4) Hold; the "clip the zone" caption fades in with a subtle pulse on the 8 balls centered below the line (`plate_z_n` < 1.5).
**Speaker's data note.** Statcast puts a pitch in zones 7–9 if any part of the ball touches the bottom third, which is why 8 of the 28 sit centered just under the line. Heights are scaled to each hitter's own zone so all 28 visibly touch the bottom row; the raw-height alternate shows why that matters. If your clips don't run in date order, reorder `video_order` in `cz1_28.csv` to match.

---
## Scene 3 · The count board (≈ 6 s)
**On screen.** None of the 28 came with two strikes · 9 on the first pitch · 15 with Nola behind in the count
**Visual.** Balls (0–3) × strikes (0–2) grid; gray rings = all 2026 changeups in that count (area = pitches), red dots = the 28. Reference `ref/dp_uc65_r3_count_board.png`.
**Data.** `data/dp_uc65_cz1_28.csv` (`count`), `data/dp_uc65_pitchmap_2026.csv` (`count`)
**Animation cue.** Gray rings draw; red dots drop into their counts; the empty two-strike row dims last with the title.
**Speaker's data note.** The changeup steals strikes when hitters are looking for something else early or with Nola behind; it isn't how he finishes them.

---
## Scene 4 · Five cards (≈ 15–20 s; Claude Design may pick 3–4)
Each card: title, one big number, one line, one context line. Optional chart behind each card (reference PNGs).

**Card A · An early-count regular vs lefties** — **23.1%** of his 0-0 and 1-1 pitches to lefties were changeups · 2nd of 30 Phillies starter seasons since 2015 · behind only his own 2023 (24.1%)
  Chart: `ref/dp_uc65_r4_early_count.png` · data `dp_uc65_ch_usage_by_year.csv` (metric `ec1_ch_usage_0-0_1-1`, stand L), `dp_uc65_ch_pool.csv` (`ec1_lhb`).
**Card B · Set it up, then the curve** — **13.0%** of his two-strike pitches to lefties were changeups (vs 23.1% early) · Changeup → curve: +1.8 runs per 100 follow-ups vs lefties (career, n 535)
  Chart: `ref/dp_uc65_r5_early_vs_late.png` · data `dp_uc65_ts1_two_strike_groups.csv`; the sequencing line is inherited from `uc-pps-040` (SQ-2 setup lift).
**Card C · It lives low** — **48%** of his changeups finished below the zone · 24% in the bottom third · Bottom-third changeups taken for strikes: 23% (5th of 30)
  Data `dp_uc65_zn1_location_by_year.csv`, `dp_uc65_ch_pool.csv`.
**Card D · The catch** — **22.1%** of his first pitches to lefties were changeups (ties his career high) · only 40% of those were strikes — a career low
  Chart: `ref/dp_uc65_r6_first_pitch.png` · data `dp_uc65_fp1_first_pitch.csv`.
**Card E · The July pivot** — **12.6% → 20.1%** changeup share, before and after 7/05 · Changeup vs lefties in 2026: .263 wOBA · +0.6 runs per 100
  Inherited from `uc-pps-040` (prior re-read); result line from `dp_uc65_ch_kpis_by_year_stand.csv`.
**Animation cue.** Cards slide up one at a time; the big number counts up; the context line types in. Card D is the honest one: keep it in if the video is shown to analysts.

---
## Scene 5 · Outro (≈ 3 s)
**On screen.** Statcast · Phillies house log · uc-pps-041
**Visual.** The hero map shrinks to a corner thumbnail; source line set small.
