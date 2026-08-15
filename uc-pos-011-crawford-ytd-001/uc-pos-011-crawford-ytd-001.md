# uc-pos-011-crawford-ytd-001 — Justin Crawford Year-to-Date Read

**UC #35 · `dp_uc34` · Phillies Offense (`pos`) · submitted 2026-08-15 · delivered 2026-08-15**
<br>Requester / DPO: Kellen Short · Validator disposition: **GO**, 0 blocking, 4 conditions (see `01_strategy_intake.md`)

---

## Use case as submitted — verbatim

> Justin Crawford has supposedly turned a corner and begun to establish himself as he adjusts to life
> in the Big Leagues. Since roughly mid-June, he has been hitting the ball much better with his
> batting average slowly climbing up, his OBP bouncing back, and his wOBA coming up. These are
> assumptions that should be tested first. Assess his performance against those KPIs and any other
> top-line results before digging into why that could be. His profile tends to be a
> high-swing/high-chase but low-whiff hitter who puts a lot of balls in play and uses his speed to
> beat them out for hits. Check his ground ball rate and average launch angle on BIPs since those have
> frequently been cited throughout his development path as indicators he will not succeed at the
> big-league level. Consider if his performance against LHP/RHP has changed particularly since this
> could coincide with the acquisition of Derek Hill and reduced opportunities for Crawford against
> LHP. Also if there are specific pitch_types or pitch_groups he is having success against, call that
> out as well.
>
> One of the ways to contextualize Justin Crawford's performance is against other Phillies CFs in the
> Statcast era. I am pasting below a code snippet to identify that context window. I think I would
> like to see the cumulative line graphs of the context layer greyed out with Crawford's 2026
> performance highlighted for the three results KPIs (BA, OBP, wOBA) to get a sense of how Crawford is
> tracking relative to Phillies centerfielders of the last decade or so.
>
> I would like to see a pdf report as an output and expect a fully governed package to be delivered.
> If it makes sense, I would like to explore an interactive dashboard as a delivery method. Other
> output types are acceptable too. Any other additions to the data product can be driven by the data
> product organization.

### Context-window definition — as supplied, transcribed without alteration

```python
cf8 = pps.groupby(['game_year','fielder_8'], as_index=False
       ).agg(uq_cf_games = ('game_pk','nunique')
       ).merge(pos.groupby(['player_name','batter'], as_index=False
                ).agg(pitches = ('des','size')),
               left_on=['fielder_8'], right_on=['batter'], how='inner',
               suffixes=('_cf8','_pos'))
# Crawford has played 110 games in Center Field for the 2026 Philadelphia Phillies
# Contextualize against any Phillies CF who appeared in half of the games in a single year (81)
cntxt_cf8 = cf8[cf8.uq_cf_games > 80]
pps_cf8 = pps.groupby(['game_pk','game_year','fielder_8'], as_index=False
           ).agg(cf8_pitches = ('des','size')
           ).merge(cntxt_cf8, on=['game_year','fielder_8'])
cntxt = pps_cf8[pps_cf8.cf8_pitches > 10].merge(
            pos[pos.player_name.isin(cntxt_cf8.player_name.unique().tolist())],
            on=['game_year','game_pk','batter','player_name'], how='inner',
            suffixes=('_pps','_pos'))
level = ['player_name','game_year','stand']
kpis  = ['plate_apps','bbrate','ba','obp','woba']
z = nresults(level, cntxt)
```

**Implemented as `dp_uc34_kernel.cf_context_pool(pos, pps, min_cf_games=80, min_cf_pitches=10)`.**
Thresholds unchanged. The `stand` level was dropped from the published pool — Crawford has a single
value (`L`) and grouping by it adds a dimension with no contrast for the subject while splitting the
comparators. The 110-game figure reproduces exactly (verification §8).

---

## Requirements

| ID | Requirement | Satisfied by |
|---|---|---|
| **RC-1** | Test the four submitted assertions **before** explaining anything | Report §1 — verdict column on all four |
| **RC-2** | Results and approach at a single reportable grain | `dp_uc34_monthly_master.csv`, 44 cols × 6 months |
| **RC-3** | A denominator beside every rate | shipped on every receipt |
| **RC-4** | Hitter approach must not be conflated with pitcher intent | `fpsr` / `in_zone_rate` labelled opponent metrics in kernel, report and dashboard |
| **RC-5** | A requester-supplied, outcome-selected breakpoint must be priced both ways | `dp_uc34_breakpoint_scan.csv`, 9 candidates |
| **RC-6** | Every number traceable to a governed KPI | `04_engineering_build.md` lineage |
| **CR-1** | Ground-ball rate and launch angle on BIP, against a benchmark | `battedball_profile` + 217-season population pool |
| **CR-2** | Separate results from contact quality | BABIP / ISO vs `xwobacon_bip` / `mean_la` / hard-hit |
| **CX-1** | Context vs Phillies CFs, Statcast era, per the supplied snippet | `cf_context_pool` — 8 comparator seasons |
| **CX-2** | Cumulative BA / OBP / wOBA, context ghosted, Crawford highlighted | `running_line_pa` extended to BA and OBP; Fig 1 + live dashboard toggle |
| **PL-1** | Test whether the platoon mix explains the improvement | `platoon_counterfactual` — direct standardisation |
| **AR-1** | Call out pitch types and groups | `dp_uc34_pitch_type_season.csv`, `_pitch_group_window.csv` |
| **OUT-1** | PDF report | `dp_uc34_crawford_ytd_report.pdf` |
| **OUT-2** | Interactive dashboard | `dp_uc34_crawford_ytd_dashboard.html` — self-contained, no network |
| **OUT-3** | Fully governed package | 00–07 receipts, 17 CSVs, 127/127 verification |

## Additions driven by the data product organization

Not requested; added because the analysis required them.

| Addition | Why |
|---|---|
| **Breakpoint sensitivity scan** | "Roughly mid-June" was chosen after observing the outcome. A mid-May boundary reverses the sign. Without the scan the report would assert something the data does not support at the stated confidence |
| **BABIP and ISO on `nresults_unrounded`** | "Hitting the ball better" is unadjudicable without separating outcome from impact. They are the two columns that turn the premise from unfalsifiable to testable |
| **217-season population benchmark** | "High-swing / high-chase / low-whiff" and "GB rate and launch angle are the knocks" are comparative claims with no comparison attached. Percentiles supply one |
| **Archetype cohort** | Percentiles say where he sits; the nine lowest launch angles say what that position has historically been worth over a full season |
| **PL-1 direct standardisation** | The platoon question was posed causally. Eyeballing splits cannot answer it; a counterfactual can |
| **Half-month platoon exposure** | The window-grain answer (no effect) and the half-month answer (severe August shielding) are both true. Reporting either alone misleads |
| **Ground-ball quality receipt** | The speed hypothesis is testable — exit velocity down, batting average up — and it is the mechanism behind the whole BABIP move |
| **Governance tab on the dashboard** | Three of the most quotable cells in this product are below the reliability floor. The floors had to be as reachable as the numbers |
