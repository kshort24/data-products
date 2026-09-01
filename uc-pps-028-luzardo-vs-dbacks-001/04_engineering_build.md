# 04 · Engineering Build — uc-pps-028 (UC #39 / dp_uc39)

**Layer 3 agents:** `technical-lineage-builder` · `data-engineer` · `data-quality-engineer` · `eda-agent`
**Status: ✅ PASS — pipeline executed against the live plane on 2026-09-01.**

---

## 1 · Execution record

| | |
|---|---|
| Build | `dp_uc39_luzardo_vs_dbacks.py` — 1,090 lines, executed 2026-09-01 |
| Verification | `dp_uc39_verification.py` — **195/195 PASS · 0 FAIL** |
| Dashboard | `dp_uc39_build_dashboard.py` → offline HTML + artifact variant |
| PDF | `markdown` → `weasyprint`, Phillies-branded CSS, 9 pages |
| Receipts | **30 files** in `out/` (24 CSV, 5 PNG, 1 JSON payload) |
| DQ | 28 rules, **0 FAIL**, 2 WARN (both carried open defects) |
| Plane | `MLB_DATA_ROOT` mounted; every published number computed this session |

**Environment.** `pyarrow` is absent from the device VM and would not install to `$HOME` (the
`/sessions` allowance is full at 9.2 GB once the whole `MLB` folder is granted).
`pip install --target /tmp/pylibs --no-cache-dir pyarrow` with `TMPDIR`/`PIP_CACHE_DIR` redirected
to `/tmp` succeeds, and `PYTHONPATH=/tmp/pylibs` carries it. **This extends the `uc-pps-027`
environment note** — the previously recorded recipe fails now because pip's *cache* also lands on
the full volume; both must be redirected, not just the target. `weasyprint` cannot be installed on
the device VM at all (native pango/cairo dependencies), so the PDF is the one step built in the
cloud container from staged inputs and committed back.

## 2 · technical-lineage-builder — column-level lineage

**CN-1 · start-xwOBA dispersion**
```
phils_2026.parquet
  .estimated_woba_using_speedangle  (Statcast, verbatim)
  → filter phillies_role=='pitching' ∧ game_type=='R' ∧ pitcher∈cohort
  → dedup(game_pk, at_bat_number, pitch_number)
  → to_numeric(errors='coerce')
  → groupby(game_pk).mean()                            = start xwOBA   [grain: start]
  → filter start.pa >= 15 ∧ start.game_date >= window
  → std(ddof=0)                                        = cn1_xwoba_sd  [grain: pitcher × window]
```

**CN-2 / CN-3 · floor and blow-up rates**
```
phils_2026.parquet .events, .bat_score, .post_bat_score
  → pa_last(game_pk, at_bat_number)                    [grain: PA]
  → events.map(OUTS_MAP).sum()                         = start.outs
  → (post_bat_score − bat_score).clip(0).sum()         = start.runs
  → mean(outs>=15 ∧ runs<=3)                           = cn2_floor_rate
  → mean(runs>=5 ∨ outs<12)                            = cn3_blowup_rate
```

**AR-1 · opponent tier**
```
phils_2026 ∪ phils_2025 ∪ luzardo.parquet(2019-24)
  → derive opp = away_team if home_team=='PHI' else home_team          (2025-26)
    derive opp = away_team if inning_topbot=='Top' else home_team      (career, org-agnostic)
  → filter opp ∈ {AZ, ARI}
  → pa_last → des
  → strip leading replay-review clause  (defect D-2 fix)
  → split on the event-verb list → modal name per batter id            = batter_name
  → groupby(batter).max(game_date) >= '2025-01-01'                     = tier
```

**Cohort membership**
```
phils_2026 (all Phillies pitching)
  → sort(game_pk, inning, at_bat_number, pitch_number).groupby(game_pk).first()
  → .pitcher                                            = starter of record   [grain: game]
  → groupby(starter).nunique(game_pk) >= 8               = cohort
```

## 3 · data-engineer — receipts emitted

| Receipt | Contents |
|---|---|
| `season_line.csv` | 2025 full / 2026 full / 2026 H1 / 2026 H2 — 22 columns |
| `start_log_2026.csv` | 27 starts × 18 columns, the atom of the CN family |
| `consistency_cohort.csv` | 5 pitchers × CN-1…CN-6 + level metrics, window 2026-05-01 |
| `consistency_ranking.csv` | tidy long: axis × pitcher × value × rank × cohort size |
| `consistency_breakpoint_scan.csv` | 8 boundaries × 8 axes × (rank, value) — **the falsification receipt** |
| `consistency_full_season_control.csv` + `_ranking_full_season.csv` | the uncut-season control |
| `uc17_reproduction_check.csv` | 17 published H1 figures vs this build |
| `uc17_tripwire_closure.csv` | 16 watch items, H1 → H2 with verdicts |
| `arsenal_h1_h2.csv` | 2025 / H1 / H2 × pitch × 13 columns |
| `process_kpis_h1_h2.csv` | the `uc-pps-017` §4 panel, extended |
| `tto_h1_h2.csv`, `by_stand_h1_h2.csv`, `monthly_2026.csv`, `battery_2026.csv` | splits |
| `workload_rest_2026.csv` | pitch counts, days' rest, cumulative load |
| `ari_history_line.csv`, `ari_start_20260410_mix.csv`, `ari_h2h_batters.csv` | opponent lens |
| `attack_plan_by_stand.csv`, `two_strike_menu_by_stand.csv` | the actionable panel |
| `dq_scorecard.csv`, `freshness_manifest.csv` | governance |
| `payload.json` | the single source every rendered artifact reads |
| `fig1…fig5 .png` | consistency map, start trend, arsenal drift, TTO, breakpoint scan |

**No file from a prior UC is overwritten.** All outputs are namespaced `dp_uc39_*` and written to
this package's own `out/`, not the shared repo `out/`.

## 4 · eda-agent — the finding the design did not anticipate

Hard-hit rate rose **30.5% → 38.2%** across the break while xwOBA *improved* .269 → .251. The
batted-ball profile explains it and the explanation is the report's §4:

| | H1 (285 BIP) | H2 (123 BIP) |
|---|---|---|
| avg exit velocity | 85.9 | **88.1** |
| avg launch angle | 6.2° | **12.6°** |
| barrel rate | 5.3% | **8.9%** |
| ground-ball share | 52.3% | 44.7% |
| **BIP per PA** | .613 | **.591** |
| **K%** | 29.2% | **32.2%** |
| xwOBA **on contact** | .334 | .328 |

**He allows better-struck contact and less of it.** The strikeout gain pays for the contact-quality
loss — which makes the profile *conditional* rather than simply improved, and gives the report a
falsifiable watch item instead of a compliment.

## 5 · data-quality-engineer — scorecard

28 rules · **0 FAIL** · 2 WARN (`O-5`, `O-8` — both pre-existing, both disclosed in every artifact).
Full scorecard: `out/dp_uc39_dq_scorecard.csv`. Freshness manifest: `out/dp_uc39_freshness_manifest.csv`,
including the explicit `ARI confirmed lineup = NOT AVAILABLE` row.
