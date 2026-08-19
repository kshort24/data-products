# uc-pos-012-nola-alcantara-showdown-001 — If Aaron Nola Against the Marlins Were a Phillies Hitter

**UC #36 · `dp_uc35` · Phillies Offense (`pos`) · submitted 2026-08-18 · delivered 2026-08-19 (pre-game)**
<br>Requester / DPO: Kellen Short · Validator disposition: **GO**, 0 blocking, 5 conditions (see `01_strategy_intake.md`)
<br>Game context: Aaron Nola (PHI) vs Sandy Alcantara (MIA) · Citizens Bank Park · 2026-08-19 18:05 ET

---

## Use case as submitted — verbatim (prose)

> **Aaron Nola and Sandy Alcantara starting against one another** · *Aaron Nola against the Marlins*
> · value_stream = Phillies Offense · Level of Granularity = Phillies RHB with plate_apps similar to
> Nola against Miami RHB · kpis = Slash Line, wOBA, K Rates, Whiff, Chase, and Hard Hit Rate, Add
> Barrel Rate · data_viz = prose
>
> What if the "batter" that Aaron Nola elicited in terms of offensive output by season [were] just a
> straight line across all years of this box plot — instead of the current format where he is called
> out as his own point for each of his own game_year level performance against MIA. Let's change that
> so it is just a constant. Same with Wheeler. Then highlight the individual Bryce Harper against
> Marlins in the Statcast era.
>
> Which connects us to the flip side of this old-school National League East showdown between two
> gunslingers. Dominant RHP who are destined for the Hall of Very Good more likely than the Hall of
> Fame. Sandy Alcantara has thrown more [pitches] to the Phillies offense in the Statcast era than
> [anyone]. Bryce Harper has faced him third most of any pitcher since 2015. The only other real
> competitor could be Max Scherzer or Jacob deGrom. One guy was Harper's teammate for a good chunk of
> Mad Max's appearance in the pos dataset. The other was oft-injured or starred in years when Harper
> missed time due to injury.
>
> prose: Take the description of this graph. Generate Business Intelligence. Show me a scatter plot
> at discrete season levels with the highlight on Aaron Nola against the Marlins. Facet Columns by
> Batter Stand.
>
> I would like to see a pdf report as an output and expect a fully governed package to be delivered.
> If it makes sense, I would like to explore an interactive dashboard as a delivery method. Other
> output types are acceptable too. Any other additions to the data product can be driven by the data
> product organization.

### Data-plane snippet — as supplied, transcribed without alteration

```python
df = pd.concat([nola[(nola.home_team == 'MIA') | (nola.away_team == 'MIA')]
                ,pos[pos.player_name != 'Nola, Aaron']
               ])
df['nola_color'] = np.where(df.player_name == 'Nola, Aaron', "Noles", "Phillies Hitters")
level = ['player_name','game_year','nola_color']
z = nresults(level,df
            ).merge(whiff_rate(level,df), on=level, how='left', suffixes=('','_wr')
            ).merge(runs_created(level,df), on=level, how='left', suffixes=('','_rc'))
kpis = ['plate_apps','ba','obp','slg','ops','woba','runs_created','rc_per_pa']
z['rc_per_pa'] = z.runs_created/z.plate_apps
criteria = 15
fig = px.box(z[z.plate_apps > criteria][level+kpis].round(3), x='game_year', y='rc_per_pa',
             color='nola_color', title="If Aaron Nola against the Marlins were a Phillies hitter",
             template='plotly_dark', points="all", hover_data=level+kpis, ...)
fig.update_xaxes(range=[2014, 2027]); fig.update_yaxes(range=[0, 0.31])
```

**Implemented with governed corrections, each logged:** the snippet's `nola` frame becomes
`SB-1 synthetic_batter(pps, 'Noles', opponent='MIA', pitcher=605400)` (id lock instead of name
filter; the MIA filter keys on the *batting* team, not home/away alone, which would also match
PHI@MIA innings where PHI bats) · `nresults` → `nresults_unrounded` (D4) · `whiff_rate` →
`whiff_rate_fix` (D1) · `criteria = 15` → HD-1 ruling (derived floor 27/11/12) · `.round(3)`
applied at publication only. The box-color design is superseded by HD-2 (constants), per the prose.

---

## Requirements

| ID | Requirement | Satisfied by |
|---|---|---|
| **RC-1** | Test the prose's factual claims before narrating them | Report §2 verdict table P1–P5 |
| **RC-2** | Full KPI family: slash, wOBA, K, whiff, chase, hard-hit, + barrel | `KF-1 kpi_family()`; every published grain |
| **RC-3** | Denominator beside every rate | PA/pitches/swings/ooz/bips on all receipts |
| **HD-1** | PA floor = Nola's minimum plate_apps in the dataset (human-DPO ruling) | `floor_derivation{,_stand}.csv` — 27 / 11 L / 12 R, derived not keyed |
| **HD-2** | Box plot: Nola & Wheeler as career constants; Harper-vs-MIA highlighted | Fig 1 + `boxplot_population.csv` + career receipts |
| **RC-5** | Season scatter, Nola highlighted, faceted by batter stand | Fig 2 + dashboard tab 2; per-stand floors per HD-1 |
| **RC-6** | The Alcantara flip side as BI: exposure record, Harper rank, Scherzer/deGrom context | Figs 3–4; `pitcher_exposure_rank_top25.csv`, `harper_pitcher_rank_top25.csv`, H2H receipts |
| **RC-7** | Every number traceable to a governed KPI | `04_engineering_build.md` lineage; 79/79 verification |
| **OUT-1** | PDF report | `dp_uc35_nola_alcantara_report.pdf` |
| **OUT-2** | Interactive dashboard | `dp_uc35_nola_alcantara_dashboard.html` — self-contained, vendored Chart.js |
| **OUT-3** | Fully governed package | 00–07 receipts, 24 CSVs + 5 figures, verification suite |

## Additions driven by the data product organization

| Addition | Why |
|---|---|
| **Premise verdict table (P1–P5)** | Three of the prose's factual claims are falsified or out-of-plane (Scherzer leads the exposure record; Harper-vs-Alcantara is #1 in-frame; no 2025 Nola-MIA meeting). Correcting them silently would be a governance failure; asserting them would be a factual one |
| **Wheeler pre-PHI coverage** (`wheeler.parquet` 2017–19) | "Same with Wheeler" on `pps` alone would silently mean *2020 onward*; the cache makes the constant a true career-vs-MIA number (593 PA), with disjointness verified |
| **The 7/28 duel receipt** | The two subjects already met this season (MIA 1–0, game 823838) — discovered in-frame; it converts the report from trivia to a rematch preview |
| **Stand-grain career splits** | The facet ask exposes the real finding — Nola's Marlins mastery is lefty-shaped (.267 wOBA/262 PA), opposite his 2026 league-wide lefty leak (uc-pps-021) |
| **`player_name` semantics receipt** | The DPO's own hover label ("ambiguous column!") is right: the column means batter on `pos` and pitcher on `pps`. Receipted, and the root of open item O-10 |
| **Manual carry-in log for display names** | Scherzer/deGrom ids have no local name authority; the names ship annotated and logged rather than silently trusted (dp_uc25 lineup precedent) |
| **Falsifiable game-day calls (report §6)** | Turns the product into something the 8/19 result can grade — the standing backtest hook (07) |
