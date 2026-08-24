# 06 — Consumer Success

**Department:** Consumer Success · **Agents:** `analytics-enabler` · `consumer-onboarding-agent` ·
`query-builder` · **Use Case:** `uc-pps-026-cortes-acquisition-001` · **Date:** 2026-08-20

---

## 1. consumer-onboarding-agent — persona guides

**Manager (Don Mattingly).** Your section is report §"Manager — deployment" and dashboard V1.
The five answers you asked for, in order: he is a proven bulk/multi-inning arm (2019 receipt),
put him on an 18-BF leash (TTO receipt), point him at lefty stretches (platoon receipt), don't
hand him a one-run ninth yet (leverage history receipt), and don't build rest days into the plan
(rest receipt). Every claim carries its PA; the two that are profile-driven rather than
experience-driven say so in the text.

**Battery.** Your section is report §"Battery — pitch selection" and dashboard V2. The one-line
card: *sweeper away to lefties, cutter-in/changeup-away to righties, fastball up when it goes up
at all — and stop throwing lefties the belt-high four-seam.* The behind-in-count cutter tell
(44.8%) is worth knowing about yourself before opponents' advance rooms find it.

**Pitching department.** Your section is report §"Pitching department — monitoring cues" and
dashboard V3 (pitch-type dropdown — your own notebook pattern, productionized). The velo bands
(green ≥91.5 / yellow 90.5-91.5 / red <90.5), the IVB ≥18.5 shape floor, and the slot baseline
(`dp_uc36_mechanics_by_season.csv`) are the three receipts to pin on the wall for his rehab
bullpens.

## 2. analytics-enabler — how to use this product

- **Consumables:** `dp_uc36_cortes_acquisition_read_report.pdf` (7 pp, print-ready) ·
  `dp_uc36_cortes_dashboard.html` (open in any browser; fully offline, plotly vendored).
- **Receipts:** every number in both consumables traces to a CSV in `out/` — the figure captions
  and dashboard footer name the exact file. To re-cut an analysis, start from the receipt, not
  the figure.
- **Common queries** (against the standard frames, entity lock `pitcher == 641482`):
  - Deployment: `out/dp_uc36_appearance_log.csv` is the appearance grain — filter and
    re-aggregate rather than re-deriving from pitches.
  - "How's the return going?" — re-run `dp_uc36_cortes_acquisition_read.py` after a data
    refresh; the 2026 gap checks will fail loudly the moment 2026 rows exist, which is the
    designed signal to re-baseline (closure step, 07).
- **FAQ:** *Why no ERA/IP?* Not derivable without `gms_AI` (01 G5); appearance-grain KPIs carry
  the deployment story. *Why does 2025 look so bad?* 157 PA around an injury — directional,
  which is why every 2025 line prints its PA. *Is the Freeman thing in here?* As a context
  receipt only (`out/dp_uc36_postseason_context.csv`), exactly as the use case requested.

## 3. query-builder — starter templates

```python
# Appearance-grain deployment cut (the UD spine)
ap = pd.read_csv("out/dp_uc36_appearance_log.csv")
ap.groupby("game_year")[["is_start", "is_bulk"]].mean()

# Platoon re-cut at any grain from the pitch frame (kernel functions loaded)
vs = pd.concat([nphl[nphl.pitcher == 641482], pps[pps.pitcher == 641482]])
vs = vs[vs.game_type == "R"].drop_duplicates(["game_pk", "at_bat_number", "pitch_number"])
kpi_block(vs, ["game_year", "stand"])          # matches dp_uc36_platoon_by_season.csv

# Return-monitoring: rolling 50-pitch FF velo vs the 2024/2025 baselines
ff = vs[vs.pitch_type == "FF"].sort_values(["game_date", "at_bat_number", "pitch_number"])
ff.release_speed.rolling(50).mean().tail()
```
*(The `pitcher == 641482` lock replaces the use case's name filter — names are display, ids are
identity. The DPO's original `player_name` concat reproduces the same frame today, but the id
lock is the governed pattern.)*
