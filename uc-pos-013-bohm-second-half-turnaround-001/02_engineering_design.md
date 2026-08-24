# 02 · Engineering Design
**data-architect · kpi-calculator · eda-agent · join-validator · dq-rule-definer · metadata-mapper**

## Data architect — model & grain

One source population, five published grains, every master built by the same
`kpi_master(base, level, …)` assembler so a KPI means the same thing at every grain:

| Frame | Grain | Rows | Purpose |
|---|---|---|---|
| `career_by_year` | `game_year` | 7 | premise 5/6 context; whiff trajectory; pull-air history |
| `window_split` | `window` (pre/post break) | 2 | THE headline contrast |
| `monthly_master` / `monthly_panel` | `month` (calendar) | 6 | where the surge lives; floor flags |
| `platoon_splits` | `window × p_throws` | 4 | premise-platoon; feeds PL-1 |
| `pitch_group_window` | `window × pitch_group` | 8 | fastball/breaking/offspeed read |

Grain guards (join-validator, executed as build asserts, re-run in verification):
window PA + PA = season PA (no leak); monthly master row count == distinct months (no fan-out);
monthly PA sums to season; pitch-group PA and pitches sum to season totals; single-row entity lock
(`player_name.nunique()==1`, `stand=='R'`).

## Value stream vs data domain (the DPO's open design note)

The submitted snippet carries `dd = data_domains = vs` with the note that the two concepts need to be
separated. This build adopts the separation as follows and hands the naming decision back to the DPO:

- **Value stream** (`vs`) — the *consumer* axis: **Phillies Offense** (`pos`). Owns the use case, the
  personas in §5 of the report, acceptance criteria, and the publish decision.
- **Data domain** (`dd`) — the *source* axis: the **batting-events Statcast domain** (pitch grain,
  `events`/`description` semantics) plus the **batted-ball tracking domain** (`launch_*`, `hc_*`,
  sensor-bounded). One value stream consumes several data domains; the sensor-boundary NULL rules
  belong to the *domain*, the floors and KPI choices to the *value stream*. The weather dependency
  domain (`dom-weather-001`) already models the same split on the pitcher side.

`dd = vs` is therefore treated as a placeholder equality that happens to hold when a use case touches
a single domain slice — it does not here (tracking vs events domains have different NULL regimes), and
the receipts keep the two ledgers separate (source-profile rows are tagged by domain in `01`).

## KPI calculator — specs

**Consumed governed / inherited** (no respec): `nresults_unrounded` (D4-corrected slash+wOBA),
`whiff_rate_fix` (D1), `chase_rate_g`, `hard_hit_rate_fix` (D2, D6 retained), `barrel_rate_g`,
`fpsr_fix` (D3; APPROVED cde.fpsr, consumed), `swing_rate` (AP-2), `srfp` (AP-3), `ooz_whiff_rate`
(uc-cat-001 correction), `battedball_profile` (CR-1), `xcontact` (CR-2, O-4 naming),
`running_line_pa` (AP-6), `platoon_counterfactual` (PL-1), `pool_percentile`, `inds_unrounded`
(governed cell 17 minus rounding; O-3-exposed, shipped for reconciliation only), `runs_created`
(governed cell 14, verbatim).

**NEW this UC — all provisional pending ratification:**

| ID | Name | Spec |
|---|---|---|
| **RC-R1** | `rc_per_pa` | `runs_created / plate_apps` at the same level. Population: governed PA rows. Edge: NULL when PA==0. Why: the windows differ 377 vs 135 PA — the raw governed total is volume-confounded |
| **PA-L1** | `derive_loc` | `loc_x = C·(hc_x−125.42)`, `loc_y = C·(198.27−hc_y)`, C = 2.495671 ft/unit (cbp-spray convention). Convention asserted empirically each run: median pulled-GB loc_x < 0 for a RHB, else the build refuses to publish pull-side output |
| **PA-F1** | `pull_air_rate_fix` | Governed cell-24 boundary logic VERBATIM on derived coordinates: pull-air = pulled BIP with `bb_type != 'ground_ball'`; denominator = ALL BIP (the governed function's own choice — its unused `total_pulls` is shipped as `pull_rate` for transparency). `hc_tracked` shipped beside the rate (0 gap in 2026). Scale-invariance of the ±4.7-slope classification proven in verification §11 |
| **ZS-1** | `zone_swing_whiff` | The DPO operators verbatim: `swing_rate` and `whiff_rate` on `df[df.zone < 10]` → `swing_rate_in_zone`, `whiff_rate_in_zone`. NULL-zone rows (5) excluded from both zone populations, disclosed |
| — | `ba_risp` (+ `slg_risp`, `woba_risp`, `risp_pa`, `risp_ab`) | `nresults_unrounded` over `on_2b.notna() | on_3b.notna()` rows → terminal-pitch RISP membership (C-2). Not a new function — a governed function over a DPO-defined population |
| — | `running_line_pa.cum_slg` | additive extension (TB/AB cumulative); non-breaking, mirrors the uc-pos-011 BA/OBP extension |

## EDA notes that shaped design

April (.180 wOBA / 99 PA) is a structural crater that any pre-break aggregate carries — motivated
putting the monthly panel and the career ghost lines beside the window split rather than behind it.
Popup share (6.3% → 2.7%) surfaced in EDA and was promoted into the batted-ball story. The
post-break LHP cell (.584 wOBA / 33 PA) was identified at EDA time as the "loudest least-reliable"
split and pre-assigned its ⚠ treatment before any narrative was written.

## DQ rule definer → hand-off

Rules specified for the DQ engineer (implemented in build asserts + verification; scored in `05`):
entity lock uniqueness; window complementarity & the 13–15 Jul empty set; PA/pitch conservation at
every grain; PITCH_KEY uniqueness; sensor-boundary NULL preservation (no blanket fillna; rates NULL
below floor); coordinate-convention assertion; `truncated_pa` (O-5) and `automatic_*` counts reported;
zone-NULL symmetry between chase and z-swing denominators.

## Metadata mapper — the DPO's data dictionary honored

The submitted `data_dictionary` display names are carried onto every surface (report, dashboard,
figures): `pull_air_rate` → "Pull AIR %" (rendered "Pull-Air%"), `hard_hit_rate` → "Hard Hit %
(95+ mph EV)", `la_mu`/`ev_mu` → "Avg. Launch Angle"/"Avg. Exit Velocity" (mapped to the tracked-BIP
standard per steward ruling 3, with the all-rows `inds` figures shipped alongside), `ba_risp` →
"BA (w RISP)", `runs_created` → "Runs Created", `swing_rate_in_zone` → "In-Zone Swing Rate",
`whiff_rate_in_zone` → "In-Zone Whiff Rate". The snippet's `# (might be par?)` alias question is
resolved: the governed name is `pull_air_rate` (cell 24); `par` and `pulled_air` are aliases and do
not appear in receipts (alias-is-not-a-name rule).
