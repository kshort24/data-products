# 04 · Engineering Build — `uc-pps-030-painter-vs-braves-001`

**UC #44 · `uc-pps-030` · `dp_uc44`** · Engineering Build department (`data-engineer`)

---

## What was built

| Artefact | Lines | Role |
|---|---|---|
| `dp_uc44_kernel.py` | ~430 | Governed kernel. **Section A** verbatim from `Baseball Functions.ipynb` (via `dp_uc43_kernel`); **Section B** data access (verbatim behaviour of `mlb_data.py`); **Section C** the seven new objects |
| `dp_uc44_painter_vs_braves.py` | ~430 | The build. 24 CSV receipts + JSON payload. Refuses to run off-anchor |
| `dp_uc44_build_figs.py` | ~240 | 5 figures, every number sourced from a receipt or recomputed from the frame the receipt came from |
| `dp_uc44_build_pdf.py` | ~55 | markdown → weasyprint, Phillies CSS, figures embedded as base64 so the PDF is portable |
| `dp_uc44_build_dashboard.py` + `tpl/` | ~60 + 3 | Self-contained interactive card. No CDN, no external fetch |
| `dp_uc44_verification.py` | ~270 | 7 assertion families, 247 checks |

## Environment notes (disclosed — these shaped tooling, not analysis)

- **`device_bash` was unavailable for the entire engagement.** A Windows update dated 2026-09-08 broke the
  workspace mount on the client's machine (`sandbox-helper: no Plan9 drive shares mounted`). The house pattern
  — run the analysis in place on the client's own machine — was not available.
- **Consequence:** the data plane was staged into the cloud container (13 parquet files, ~63 MB, one call) and
  the finished package committed back. Every path in the build resolves through `data_root()`, which tries
  `MLB_DATA_ROOT` → the container mount → a relative path → the Windows path, so the same script runs
  unmodified on either machine. **No analysis decision was affected**; the cost was time and one extra copy of
  the data, and it was priced in the bid as environmental contingency.
- **The MLB repo was not a connected folder at session start.** Access was requested and granted mid-session.
  The first request timed out unanswered; the second was granted. Recorded because it is a recurring 4–6
  minute tax on any cross-repo engagement.
- `pyarrow` and `weasyprint` were not present in the container and were installed. Python 3.11, pandas 2.x,
  scipy, matplotlib (Agg).

## Build-time assertions (the build refuses to publish if these fail)

```python
assert len(ap) > 0                                  # entity lock returns rows
assert ap.player_name.nunique() == 1                # lock is pure
assert ap.player_name.iloc[0] == 'Painter, Andrew'  # lock is the right player
assert anchor == K.ANCHOR_GAME_DATE                 # a refreshed cache is a NEW game
assert (ap.game_type == 'R').all()                  # no spring, no exhibition
assert ap.duplicated(subset=['game_pk','at_bat_number','pitch_number']).sum() == 0
```

The anchor assertion is the important one. It carries this message:

> `ANCHOR MISMATCH: log ends {anchor}, build is pinned to {ANCHOR_GAME_DATE}. A refreshed cache is a new game
> — re-anchor deliberately, do not override.`

The figure builder carries one more, because a chart title is a claim:

```python
assert set(_multi.game_date) == set(post_sl[post_sl.xwoba >= 0.400].game_date), 'title claim no longer holds'
```

Figure 5's title asserts that the only two starts over .400 xwOBA are the only two with multiple home runs.
If a refreshed cache breaks that, the figure build fails rather than shipping a false headline.

## Query patterns for reuse

```python
# Grade any pitcher's arsenal against the house population, any window:
import dp_uc44_kernel as K
allp = K.load_phils(tuple(range(2015, 2027)))
subj = allp[(allp.phillies_role=='pitching') & (allp.pitcher == <MLBAM>) & (allp.game_date >= '<start>')]
for pt in subj.pitch_type.value_counts().index:
    pop = K.benchmark_population(allp, pt, throws='<R|L>')
    d   = subj[subj.pitch_type == pt]
    sw  = d.description.isin(K.SWINGS).sum(); wh = d.description.isin(K.WHIFFS).sum()
    stuff = K.scouting_grade(wh/sw, pop.whiff_rate)
    cmd   = K.scouting_grade((d.zone<=9).mean(), pop.in_zone_rate)
    print(pt, K.pitch_grade(stuff['grade'], cmd['grade']), K.grade_label(...))

# Quantify how much of a pitcher's history still applies after any date:
K.arsenal_turnover_index(before_frame, after_frame)   # then RUN THE TAG-DRIFT CONTROL

# Resolve opponent hitters with no opponent cache, from your own pitchers' rows:
#   groupby('batter') over phillies_role=='pitching' rows in the head-to-head game_pks,
#   display name = modal des-parse. Never hand-key an MLBAM id.
```

**Reusability note.** SG-1 and SG-2 are pitcher-agnostic and pitch-agnostic. They will grade Wheeler, Sánchez,
Luzardo or an acquisition target against the same population with no code change — only `throws` and the
subject filter move. That generality is why this family is worth ratifying, and why the bid priced its
specification rather than its computation.

## Receipt manifest

| Receipt | Rows |
|---|---|
| `dp_uc44_arsenal_turnover.csv` | 1 |
| `dp_uc44_arsenal_turnover_detail.csv` | 7 |
| `dp_uc44_arsenal_windows.csv` | 19 |
| `dp_uc44_atl_lineup_vs_phi.csv` | 17 |
| `dp_uc44_benchmark_population_moments.csv` | 42 |
| `dp_uc44_breaking_izr_pooled.csv` | 3 |
| `dp_uc44_defect_exposure.csv` | 6 |
| `dp_uc44_dq_scorecard.csv` | 19 |
| `dp_uc44_efficiency.csv` | 2 |
| `dp_uc44_ff_location_profile.csv` | 2 |
| `dp_uc44_freshness_manifest.csv` | 5 |
| `dp_uc44_grades.csv` | 6 |
| `dp_uc44_grades_pre_option.csv` | 6 |
| `dp_uc44_h2h_atl.csv` | 10 |
| `dp_uc44_holmes_profile.csv` | 6 |
| `dp_uc44_mix_by_stand.csv` | 36 |
| `dp_uc44_notecard_reconciliation.csv` | 4 |
| `dp_uc44_pitch_locations_post.csv` | 720 |
| `dp_uc44_pitch_map_centroids.csv` | 12 |
| `dp_uc44_pitch_map_centroids_pre.csv` | 12 |
| `dp_uc44_platoon_splits.csv` | 6 |
| `dp_uc44_splitter_vs_changeup.csv` | 2 |
| `dp_uc44_start_log.csv` | 22 |
| `dp_uc44_tag_drift.csv` | 7 |

Plus `dp_uc44_payload.json` (the single source the report, figures and dashboard all read),
5 PNG figures, and `dp_uc44_verification_log.txt`.

## Reproducing this

```bash
export MLB_DATA_ROOT="/path/to/Python Scripts/MLB"
python dp_uc44_painter_vs_braves.py     # 24 receipts + payload
python dp_uc44_build_figs.py            # 5 figures
python dp_uc44_build_pdf.py             # 10-page branded PDF
python dp_uc44_build_dashboard.py       # self-contained interactive card
python dp_uc44_verification.py          # 247/247 expected
```

Requires `data/phillies/phils_2015..2026.parquet` and `data/opponents/lhvp26.parquet`. The build refuses to
run if the anchor game is not 2026-09-12 — by design.
