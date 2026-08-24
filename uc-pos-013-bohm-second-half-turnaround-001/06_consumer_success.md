# 06 · Consumer Success
**analytics-enabler · consumer-onboarding-agent · query-builder**

## How to use this data product

Open `dp_uc37_bohm_turnaround_dashboard.html` (self-contained, no network) for exploration;
`dp_uc37_bohm_turnaround_report.pdf` for the narrative read. Every number on both surfaces comes from
the `dp_uc37_*.csv` receipts — quote the receipt, not the pixel. Anything quoted after **2026-08-22**
must state the as-of date; the season is live and the post-break window grows every night.

**The three rules that prevent misuse:**

1. Any cell marked ⚠ is below the 50-PA floor — cite it only with its PA count attached
   (post-RISP 42, post-LHP 33, post-offspeed 12, March 21).
2. `in_zone_rate` and `fpsr` describe what *pitchers* did to Bohm (RC-4). "Pitchers challenged him
   more" is correct; "he got more aggressive in the zone" from those columns is not.
3. The break split is descriptive — the window was picked after seeing the outcome. The sensitivity
   scan (`dp_uc37_breakpoint_scan.csv`) is the license to use it: the sign survives every boundary.

## Persona onboarding

**Hitting coach.** Start at *What changed → Process*, then *Pitch types*. Your headline: the
breaking-ball fix (whiff on spin 23.4% → 14.3%, SLG .239 → .460) with **no chase cost you're paying
for it** (chase on spin up 4 pts, contact way up). The §5 hypothesis table names what a
recognition-work signature looks like in this data; if a specific intervention happened in June/July,
this product can date-bound its signal on request. Watch item: pull-air *quality* (97.7 mph on 12
balls) — if that volume ever rises toward his 2022–24 ~14% share at this EV, the SLG ceiling moves.

**Manager / bench.** *Platoon* tab. The .812 SLG vs LHP is 33 PA — do not build a lineup card on it;
the sample-backed statement is that he is producing against BOTH hands and his LHP exposure *fell*
post-break (PL-1 mix effect −18 wOBA pts: the surge is understated, not flattered). RISP: .462 ⚠
on 42 PA, but opportunity share also rose (24.4% → 31.1% of PA) — some RC/PA gain is traffic, not
conversion. No shielding case exists in this data; if anything it argues more LHP at-bats.

**Front office / R&D.** *Career trajectory* + the pool percentiles. The contact skill is real and
six years monotone (whiff 26.7% → 16.0%; post-break z-whiff 6.8% ≈ 2nd percentile of 218 Phillies
hitter-seasons). The season line remains 43rd–45th percentile — the market-facing question is whether
August's contact-quality percentile (hard-hit 90th as-a-season) is the new level or a heater; the
September refresh (`07`) is armed to answer exactly that.

**Content / broadcast.** Safe lines: SLG .351 → .488; BA w/RISP .299 → .462 *("in a small sample")*;
"he almost never swings and misses — best on the team, top-2% of any Phillies season since 2015";
"it's not a launch-angle story — he's just hitting everything harder". Avoid: the .812 LHP SLG
without its PA count; any "since the break he leads…" framing built on sub-50-PA cells.

## Query patterns (against the receipts)

```python
import pandas as pd
w = pd.read_csv('dp_uc37_window_split.csv')          # THE contrast — one row per window
w[['window','plate_apps','slg','ba_risp','rc_per_pa','hard_hit_rate','whiff_rate_in_zone']]

m = pd.read_csv('dp_uc37_monthly_panel.csv')         # month-by-month, floor flags included
m[m.below_pa_floor == False][['month','plate_apps','slg','woba']]

s = pd.read_csv('dp_uc37_breakpoint_scan.csv')       # is the finding boundary-robust? (yes)
s[['breakpoint','pre_pa','post_pa','delta_slg','delta_woba']]

pg = pd.read_csv('dp_uc37_pitch_group_window.csv')   # fastball / breaking / offspeed
pg[pg.below_pa_floor == False]
```

To reproduce from raw data on the DPO's machine: `python dp_uc37_bohm_turnaround.py` (uses the MLB
repo path by default), then `python dp_uc37_verification.py` — expect 227/227.

## FAQ

**Why does BA w/RISP differ from a public split site?** Terminal-pitch RISP membership (the DPO's
operator). A runner who reaches scoring position mid-PA and is erased before the last pitch doesn't
count here.

**Why is "Avg. Exit Velocity" ~6 mph higher than my notebook's `inds` output?** `inds` averages
tracked foul balls too (O-3). This product's headline EV is tracked balls-in-play only; the
reconciliation receipt shows both.

**Why no wRC+ / OPS+?** League-context indexing needs a league table this data plane doesn't carry;
wOBA against the 218-season Phillies pool is the governed context here.

**Is the pull-air number trustworthy?** The governed function couldn't run at all (O-7). This build's
remediation executes the same boundary logic on coordinates derived by the house convention, proves
the classification scale-invariant, and asserts the handedness convention on every run — but it is
provisional until the DPO ratifies the derivation. Volume conclusions (flat, low) are robust; treat
the exact level (10.6%) as provisional.
