# 02 — Engineering Design
## uc-pps-019 · data-architect + kpi-calculator specs

## A. Model
Flat pitch-grain frame (one row per pitch), entity-locked and deduped per 01. Derived PA-grain frame = last pitch row per `game_pk + at_bat_number` (carries `events`, score-after). All panels aggregate from these two grains. No new physical tables; receipts to `<MLB repo>/out/` as `dp_uc21_*.csv`, figures copied into this package folder.

## B. Inherited KPIs (locked — copied verbatim from dp_uc17, which inherited from Baseball Functions via dp_uc11)
`get_stats` / `nresults`, `whiff_rate`, `chase_rate` (+ in-zone), `putaway_rate`, `fpsr`, `hard_hit_rate` — zero design cost, zero redefinition.
Also inherited from dp_uc17's provisional set (PD-1..PD-7): outs/IP from event map, runs-on-mound (RA9), FIP, CSW rate, TTO split, battery split, count-leverage funnel. Same caveats apply (IP ±~1 out vs official; RA9 is not ERA).

## C. NEW KPI specs (kpi-calculator; provisional pending human-DPO ratification)

### QR-1 — Quick-Resolution Rate (the use-case question)
- **Plain language:** Of the plate appearances a pitcher finishes, what share end within the first three pitches of the PA?
- **Formula:** `QR-1 = count(PA where final_pitch.pitch_number <= 3) / count(PA)`
- **Population:** Completed PAs only — final pitch row has `events` not null and not `pickoff_1b` (locked PA definition from `get_stats`). Pitch-grain nulls in `pitch_number`: none (01).
- **Grain:** season-year (2025 vs 2026), month (2026), start (2026). Optional dimension: `stand`.
- **Edge cases:** (a) PAs ending on a runner event (caught stealing / pickoff at non-1B bases) count at the pitch on which they end — they are resolved PAs by the locked definition; (b) truncated PAs at inning end inherit the same rule; (c) intentional walks resolve at low pitch counts and slightly inflate QR-1 — count reported if material.
- **Benchmark population:** Phillies 2026 staff (≥500 pitches) — a QR-1 number means nothing without staff context (house rule).

### QR-2 — Pitches per PA (efficiency companion)
- **Formula:** `pitches / PA` at the same grains. Sanity-couples with QR-1 (they should move together).

### QR-3 — Quick-Resolution Quality
- **Plain language:** When PAs end early, does the pitcher win them? Early contact is only a virtue if it's weak contact.
- **Formula:** `nresults` + mean xwOBA computed separately over PAs resolved in ≤3 pitches vs ≥4 pitches, per season-year.
- **Edge case:** ≤3-pitch strikeouts are rare by construction (3-pitch K only); the ≤3 bucket is contact/walk-light — interpret wOBA gap accordingly, don't compare K% across buckets.

### SL-1 — Scoreless-streak receipt (consistency check, not a record adjudication)
- **Plain language:** Longest run of consecutive outs recorded with zero runs scoring while Sánchez was on the mound, 2026.
- **Formula:** Order PAs chronologically; accumulate event-map outs; reset accumulator whenever `post_bat_score - bat_score > 0` on a PA. Report max accumulated outs as IP-string.
- **Caveats (material):** score-delta method charges runs to the on-mound pitcher (bequeathed/inherited runner distortion) and event-map outs ≈ official outs ±1; SL-1 **validates the plausibility** of the 50.2 IP carry-in, it does not certify the official record.

## D. Figures (all numbers must trace to a CSV receipt)
1. `dp_uc21_fig1_arsenal_yoy.png` — usage × whiff YoY (sinker/changeup/slider).
2. `dp_uc21_fig2_start_trend.png` — per-start xwOBA + runs, scoreless streak window shaded.
3. `dp_uc21_fig3_quick_resolution.png` — QR-1 by month 2026 vs 2025 baseline line + staff benchmark band.

## E. Receipts manifest (planned)
season line · start log 2026 · staff benchmark · arsenal YoY · process KPIs YoY · by-stand YoY · TTO YoY · battery 2026 · monthly 2026 · count leverage YoY · **QR by season/month/start · QR quality split · QR staff benchmark · streak receipt** · DQ scorecard · freshness manifest.
