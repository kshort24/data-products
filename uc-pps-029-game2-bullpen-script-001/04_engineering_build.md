# 04 · Engineering Build — `uc-pps-029-game2-bullpen-script-001`

**UC #43 · `uc-pps-029` · `dp_uc43` · v1.0.0**
**Agents:** `data-engineer`, `technical-lineage-builder`, `query-builder`

## What was built

| File | Role |
|---|---|
| `dp_uc43_kernel.py` | The governed kernel. **Section A** = verbatim `Baseball Functions.ipynb`; **Section B** = verbatim `Bullpen_Functions.ipynb`; **Section C** = new to this UC (BS-1/2/3, OP-1, loaders, `two_prop_z`). Section A and B are not edited — their defects are measured, not fixed. |
| `dp_uc43_bullpen_script.py` | The build. Loads, asserts, computes every KPI, writes ~28 CSV receipts, 4 figures' worth of inputs and a JSON payload. Reproducible end to end. |
| `dp_uc43_build_figs.py` | 4 matplotlib figures, Phillies palette, every number traced to a receipt. |
| `dp_uc43_build_pdf.py` | markdown → HTML (`markdown`, tables ext) → `weasyprint`, Phillies CSS. House-standard path. |
| `dp_uc43_build_dashboard.py` + `tpl/` | Assembles the self-contained dashboard from `tpl/style.css`, `tpl/body.html`, `tpl/app.js` and a slimmed payload. Emits two variants: the standalone repo copy and a skeleton-free copy for hosted publication. |
| `dp_uc43_verification.py` | 6-family independent harness. |

## Environment notes (disclosed — these shaped tooling, not analysis)

- **`device_bash` failed again** (`no Plan9 drive shares mounted under /mnt/.virtiofs-root/shared`) — the
  third consecutive session in this pairing. Per `uc-pos-016 v1.1.0` this is now treated as the base case,
  not a contingency. Data reached the container via `device_stage_files` only.
- **`device_request_folder_access` on the MLB data plane was the first action of intake**, per the standing
  recommendation. It was granted, and it is what made the cross-repo build possible at all — the control
  plane alone contains no data.
- **Egress was partially open this session**, unlike the previous two: PyPI reachable (`pyarrow`,
  `weasyprint`, `markdown`, `playwright` all installed), **MLB StatsAPI blocked** (`403` at the proxy). The
  open PyPI path is why `pq_reader.py` was not needed this time and why the PDF went through weasyprint rather
  than a reportlab substitution. The blocked StatsAPI path is why the opponent starter's identity is inferred
  rather than looked up.
- **Fonts:** the dashboard links Google Fonts. That host is unreachable from the sandbox, so the local render
  used fallbacks; the published page will use the specified faces. Real fallback stacks are declared for
  every face.

## Build-time assertions (the build refuses to publish if these fail)

```python
assert str(pps.game_date.max())[:10] == '2026-09-11'      # anchor is the last logged game
assert set(pps.phillies_role.unique()) == {'pitching'}    # no batting-row contamination
assert set(pps.game_type.unique()) == {'R'}               # regular season only
assert 'wBB' in pps.columns                               # wOBA weights merged on MLB
assert 'wBB' not in lhv.columns                           # and NEVER on AAA  (DQ-5)
assert len(relievers) == 5                                # the anchor game used five, not four
assert len(season) > 0                                    # D-8 remediation actually worked
assert len(nine) > 50                                     # enough regulation games for the BF benchmark
assert len(opp_games) == 3                                # opposing starter's three 2026 looks
assert len(od) == 9                                       # a nine-man order resolved from des-parsing
```

The `len(season) > 0` assertion exists **because of D-8**. Without it the build would have produced a
complete, well-formatted, entirely empty set of bullpen receipts and shipped them.

## Query patterns for reuse

```python
# Availability ledger for any target date, any pen:
from dp_uc43_kernel import load_pps, appearance_summary, add_rest_days, add_rolling_workload, \
                           pitcher_season_workload, bullpen_availability_tier
apps = add_rolling_workload(add_rest_days(appearance_summary(load_pps(), mcgs_func=mcgs)))
apps['is_start'] = apps['is_start'].fillna(False).astype(bool)      # D-8 — required, every time
season = pitcher_season_workload(apps, relievers_only=True)

# Price any script:
from dp_uc43_kernel import script_capacity
detail, total = script_capacity(['Mayza, Tim','Mayza, Tim', ...], mean_bf, max_bf, mode='ceiling')

# Re-derive the requirement side for a different club or season:
gm = apps.groupby('game_pk').batters_faced.sum()
required = gm[apps.groupby('game_pk').inning_exited.max() == 9].median()
```

## Receipt manifest

| Receipt | Contents |
|---|---|
| `appearance_ledger.csv` | L1 — every 2026 Phillies pitcher-appearance with rest and rolling load (632 rows) |
| `season_norms.csv` | L2 — arm-season relief norms (26 relievers) |
| `anchor_game_ledger.csv` | the 2026-09-11 game, with the client's "named as spent" flag |
| `availability_D1.csv` / `availability_D2.csv` | BS-1 under both date framings |
| `date_framing_sensitivity.csv` | which tiers move, and how many |
| `multi_inning_propensity.csv` | BS-3, all nine arms, MLB + AAA tiers labelled |
| `script_coverage.csv` | BS-2 per-arm ask vs average |
| `script_capacity_modes.csv` | BS-2 both scripts × both modes |
| `staff_game_workload.csv` | per-game staff BF/pitches/arms — the 37-BF benchmark |
| `bullpen_game_precedents.csv` | the two 2026 bullpen games, BF per arm |
| `mayza_opener_log.csv` / `_platoon.csv` / `_mix_by_stand.csv` / `_tto.csv` | the opener evidence, incl. the OP-1 null |
| `holman_appearances.csv` / `_mix_by_stand.csv` / `_whiff_chase.csv` / `_counting_by_stand.csv` / `_velo_by_month.csv` / `_fpsr.csv` / `_putaway.csv` / `_pitch_extract.csv` | the full AAA supporting tier, 348-pitch extract included |
| `atl_order.csv` | the nine-man order with per-hand batting sides and the switch-hitter flag |
| `h2h_reliever_vs_atl.csv` | every reliever × every Braves hitter, PA printed |
| `opp_starter_games.csv` / `_by_game.csv` / `_by_stand.csv` / `_arsenal_drift.csv` / `_whiff_chase.csv` | the inferred opposing starter |
| `freshness_manifest.csv` | source dates + the manual carry-ins |
| `dq_scorecard.csv` | 12 checks across 8 dimensions |
| `defect_exposure.csv` | 10 known/new defects measured against this build |
| `verification_results.csv` | 179 checks, 6 families |
| `payload.json` | the dashboard's data, slimmed |
| `fig1..fig4 .png` | the four report figures |
