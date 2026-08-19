# 04 · Engineering Build
**data-engineer · technical-lineage-builder**

## Pipeline

```
data/phillies/phils_2015..2026.parquet ─┐
data/opponents/wheeler.parquet ─────────┤  dp_uc35_kernel.load_frames / load_opponent
data/opponents/alcantara.parquet ───────┤  (S/E excluded; entity-lock only for alcantara cache)
wOBA and FIP Constants.csv ─────────────┘
        │
        ▼
dp_uc35_nola_alcantara.py        → out/dp_uc35_*.csv (24 receipts) + dp_uc35_headlines.json
        │
        ├─ dp_uc35_build_figures.py    → out/dp_uc35_fig1..fig5.png   (plotly, kaleido)
        ├─ dp_uc35_build_pdf.py        → dp_uc35_nola_alcantara_report.pdf  (markdown→weasyprint)
        ├─ dp_uc35_build_dashboard.py  → dp_uc35_nola_alcantara_dashboard.html (Chart.js vendored)
        └─ dp_uc35_verification.py     → 79/79 PASS (independent recomputation, raw parquet)
```

Portable data root: `DP_UC35_DATA` env var → defaults to
`C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB` (runs on the DPO's machine unchanged).
Run order: build → figures → pdf → dashboard → verification. New files only; no prior UC output touched.

## Column-level lineage (KPI ← physical)

| Published KPI | Function (authority) | Physical CDEs | Transformation |
|---|---|---|---|
| plate_apps | `nresults_unrounded` (notebook via dp_uc34) | `events` | terminal rows ∉ NON_PA, counted `('des','size')` |
| ba / obp / slg / ops | same | `events` | count-based; AB = PA ∉ NON_AB; TB from 1B/2B/3B/HR counts |
| woba | same | `events`, `game_year`, constants CSV | seasonal weights; IBB excluded num+den; career grain = 2026 constants (disclosed) |
| krate | same | `events` ∈ {strikeout, strikeout_double_play} | K / PA |
| whiff_rate | `whiff_rate_fix` (D1 fix) | `description` | WHIFFS / SWINGS, left-merge preserves zero-whiff groups |
| chase_rate | `chase_rate_g` (governed) | `zone`, `description` | OOZ swings / OOZ pitches; null-zone rows drop from both sides (O-2) |
| hard_hit_rate | `hard_hit_rate_fix` (D2 fix) | `type`, `launch_speed` | `launch_speed ≥ 95` on `type=='X'`; untracked BIP stay in denominator (O-8, disclosed) |
| barrel_rate | `barrel_rate_g` (notebook) | `type`, `launch_speed_angle` | `== 6` on BIP; NULL on zero BIP (DV-2) |
| runs_created | `runs_created` (notebook **verbatim**) | `bat_score`, `post_bat_score`, `game_pk`, `at_bat_number` | max(post) − min(pre) per PA, summed to grain |
| rc_per_pa | KF-1 | derived | runs_created / plate_apps, unrounded components |
| entity populations | SB-1 / filters | `pitcher`, `batter`, `home_team`, `away_team`, `inning_topbot` | see 02 model table |
| exposure ranks | build script | `pitcher`, `des` (count), `events` | pitches = row count; PA = terminal rows; rank by pitches (team) / PA (Harper) |
| floors | HD-1 derivation | Noles `plate_apps` per grain | `min()`, receipted |

## Receipts index (out/)

`nola_mia_{seasons,season_stand,career,career_stand}` · `wheeler_mia_{seasons,career}` ·
`phi_hitter_{seasons,season_stand}` · `boxplot_population` · `harper_mia_{seasons,career}` ·
`alcantara_phi_{seasons,career,career_stand}` · `pitcher_exposure_rank_top25` ·
`harper_pitcher_rank_top25` · `harper_vs_alcantara_{seasons,career}` ·
`harper_vs_carryin_pitchers` · `floor_derivation{,_stand}` · `player_name_semantics` ·
`dq_scorecard` · `freshness_manifest` · `dp_uc35_headlines.json` · `fig1..fig5.png`

## Build notes

- The dashboard KPI cards initially rendered from the 4dp `headlines.json` and double-rounded
  one value (.5745 → .575 vs the receipt's .574468 → .574). Caught in QA screenshot review; cards
  now render from full-precision career receipts. Logged because it is the D4 failure mode
  recurring at the presentation layer — worth a standing rule: **surfaces round once, from the
  receipt, never from another rounded surface.**
- Plotly figure HTML previews were generated during build but are **excluded from the package**
  (they load plotly.js from CDN, violating the vendor rule); the governed interactive deliverable
  is the Chart.js dashboard.
- Kaleido in the sandbox needs an explicit Chromium path (`BROWSER_PATH`); on the DPO's machine
  plotly's default resolution applies.
